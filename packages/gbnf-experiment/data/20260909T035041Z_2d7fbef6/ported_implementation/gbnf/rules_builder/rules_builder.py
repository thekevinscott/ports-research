from __future__ import annotations

import re
import time

from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.js import char_at, to_utf16
from .is_word_char import is_word_char
from .parse_char import parse_char
from .parse_name import parse_name
from .parse_space import parse_space
from .symbol_ids import SymbolIds
from .types import (
    InternalRuleDef,
    InternalRuleType,
    make_internal_rule_def,
)

_WHITESPACE = re.compile(r"\s")


def _now_ms() -> float:
    return time.perf_counter() * 1000


class RulesBuilder:
    def __init__(self, src: str, limit: int = 1000):
        self.pos = 0
        self.symbol_ids = SymbolIds()
        self.rules: list[list[InternalRuleDef] | None] = []
        self.src = to_utf16(src)
        self.start = _now_ms()
        self._time_limit = limit
        self._parse(self.src)

    # ---------------------------------------------------------------- parsing

    def _parse(self, src: str) -> None:
        # move cursor forward until we reach non-whitespace content
        self.pos = parse_space(src, 0, True)

        while self.pos < len(src):
            self._parse_rule(src)

        # Validate the state to ensure that all rules are defined
        for rule in self.rules:
            if rule is None:
                continue
            for elem in rule:
                if elem.type == InternalRuleType.RULE_REF:
                    # Ensure that the rule at that location exists
                    rule_exists = (
                        elem.value < len(self.rules)
                        and self.rules[elem.value] is not None
                        and len(self.rules[elem.value]) > 0
                    )
                    if not rule_exists:
                        missing_rule_name = self.symbol_ids.reverse_get(elem.value)
                        missing_rule_pos = self.symbol_ids.get_pos(missing_rule_name)

                        # Skip over the ::= and any whitespace
                        while missing_rule_pos < len(src) and (
                            src[missing_rule_pos] in (":", "=")
                            or _WHITESPACE.search(src[missing_rule_pos])
                        ):
                            missing_rule_pos += 1

                        raise GrammarParseError(
                            src,
                            missing_rule_pos,
                            f'Undefined rule identifier "{missing_rule_name}"',
                        )

    def _parse_rule(self, src: str) -> None:
        name = parse_name(src, self.pos)
        self.pos = parse_space(src, self.pos + len(name), False)
        rule_id = self.get_symbol_id(name, len(name))

        # Skip over whitespace characters and find the ::= sequence
        self.pos = parse_space(src, self.pos, True)
        if not (
            char_at(src, self.pos) == ":"
            and char_at(src, self.pos + 1) == ":"
            and char_at(src, self.pos + 2) == "="
        ):
            raise GrammarParseError(src, self.pos, f"Expecting ::= at {self.pos}")
        self.pos = parse_space(src, self.pos + 3, True)

        self.parse_alternates(name, rule_id)

        if char_at(src, self.pos) == "\r":
            self.pos += 2 if char_at(src, self.pos + 1) == "\n" else 1
        elif char_at(src, self.pos) == "\n":
            self.pos += 1
        elif char_at(src, self.pos):
            raise GrammarParseError(src, self.pos, f"Expecting newline or end at {self.pos}")
        self.pos = parse_space(src, self.pos, True)

    # ---------------------------------------------------------------- symbols

    def get_symbol_id(self, src: str, len_: int) -> int:
        next_id = self.symbol_ids.size
        key = src[0:len_]
        if not self.symbol_ids.has(key):
            self.symbol_ids.set(key, next_id, self.pos)
        return self.symbol_ids.get(key)

    def generate_symbol_id(self, base_name: str) -> int:
        next_id = self.symbol_ids.size
        self.symbol_ids.set(f"{base_name}_{next_id}", next_id, self.pos)
        return next_id

    def add_rule(self, rule_id: int, rule: list[InternalRuleDef]) -> None:
        # mirrors JS sparse-array assignment: indexes past the end are filled in
        while len(self.rules) <= rule_id:
            self.rules.append(None)
        self.rules[rule_id] = rule

    def check_duration(self) -> None:
        if _now_ms() - self.start > self._time_limit:
            raise GrammarParseError(
                self.src, self.pos, f"duration of {self._time_limit} exceeded:"
            )

    # -------------------------------------------------------------- sequences

    def parse_sequence(
        self,
        rule_name: str,
        out_elements: list[InternalRuleDef],
        depth: int = 0,
    ) -> None:
        is_nested = depth != 0
        src = self.src
        last_sym_start = len(out_elements)
        while char_at(src, self.pos):
            if char_at(src, self.pos) == '"':
                self.pos += 1
                last_sym_start = len(out_elements)
                while char_at(src, self.pos) != '"':
                    self.check_duration()
                    value, inc_pos = parse_char(src, self.pos)
                    out_elements.append(
                        make_internal_rule_def(InternalRuleType.CHAR, [value])
                    )
                    self.pos += inc_pos  # Adjusting pos by the length of parsed characters
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif char_at(src, self.pos) == "[":
                self.pos += 1
                start_type = InternalRuleType.CHAR
                if char_at(src, self.pos) == "^":
                    self.pos += 1
                    start_type = InternalRuleType.CHAR_NOT
                last_sym_start = len(out_elements)
                while char_at(src, self.pos) != "]":
                    self.check_duration()
                    type = (
                        InternalRuleType.CHAR_ALT
                        if last_sym_start < len(out_elements)
                        else start_type
                    )
                    startchar_value, inc_pos = parse_char(src, self.pos)
                    self.pos += inc_pos
                    if type in (InternalRuleType.CHAR, InternalRuleType.CHAR_NOT):
                        out_elements.append(
                            make_internal_rule_def(type, [startchar_value])
                        )
                    else:
                        out_elements.append(make_internal_rule_def(type, startchar_value))

                    if char_at(src, self.pos) == "-" and char_at(src, self.pos + 1) != "]":
                        self.pos += 1
                        endchar_value, inc_pos = parse_char(src, self.pos)
                        out_elements.append(
                            make_internal_rule_def(
                                InternalRuleType.CHAR_RNG_UPPER, endchar_value
                            )
                        )
                        self.pos += inc_pos
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif is_word_char(char_at(src, self.pos)):
                name = parse_name(src, self.pos)
                ref_rule_id = self.get_symbol_id(name, len(name))
                self.pos += len(name)
                self.pos = parse_space(src, self.pos, is_nested)

                last_sym_start = len(out_elements)
                out_elements.append(
                    make_internal_rule_def(InternalRuleType.RULE_REF, ref_rule_id)
                )
            elif char_at(src, self.pos) == "(":
                self.pos = parse_space(src, self.pos + 1, True)
                sub_rule_id = self.generate_symbol_id(rule_name)
                self.parse_alternates(rule_name, sub_rule_id, depth + 1)
                last_sym_start = len(out_elements)
                out_elements.append(
                    make_internal_rule_def(InternalRuleType.RULE_REF, sub_rule_id)
                )
                if char_at(src, self.pos) != ")":
                    raise GrammarParseError(src, self.pos, f"Expecting ')' at {self.pos}")
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif char_at(src, self.pos) in ("*", "+", "?"):
                if last_sym_start == len(out_elements):
                    raise GrammarParseError(
                        src, self.pos, f"Expecting preceding item to */+/? at {self.pos}"
                    )
                sub_rule_id = self.generate_symbol_id(rule_name)
                sub_rule: list[InternalRuleDef] = out_elements[last_sym_start:]
                if char_at(src, self.pos) in ("*", "+"):
                    sub_rule.append(
                        make_internal_rule_def(InternalRuleType.RULE_REF, sub_rule_id)
                    )
                sub_rule.append(make_internal_rule_def(InternalRuleType.ALT))
                if char_at(src, self.pos) == "+":
                    sub_rule.extend(out_elements[last_sym_start:])
                sub_rule.append(make_internal_rule_def(InternalRuleType.END))
                self.add_rule(sub_rule_id, sub_rule)
                del out_elements[last_sym_start:]
                out_elements.append(
                    make_internal_rule_def(InternalRuleType.RULE_REF, sub_rule_id)
                )
                self.pos = parse_space(src, self.pos + 1, is_nested)
            else:
                break

    def parse_alternates(
        self,
        rule_name: str,
        rule_id: int,
        depth: int = 0,
    ) -> None:
        src = self.src
        rule: list[InternalRuleDef] = []
        self.parse_sequence(rule_name, rule, depth)
        while char_at(src, self.pos) == "|":
            self.check_duration()
            rule.append(make_internal_rule_def(InternalRuleType.ALT))
            self.pos = parse_space(src, self.pos + 1, True)
            self.parse_sequence(rule_name, rule, depth)
        rule.append(make_internal_rule_def(InternalRuleType.END))
        self.add_rule(rule_id, rule)
