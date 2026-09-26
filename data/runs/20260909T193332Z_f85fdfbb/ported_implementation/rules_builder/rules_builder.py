from __future__ import annotations

import re
import time

from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.utf16 import to_utf16_units
from .is_word_char import is_word_char
from .parse_char import parse_char
from .parse_name import parse_name
from .parse_space import parse_space
from .symbol_ids import SymbolIds
from .types import (
    InternalRuleDef,
    InternalRuleDefAlt,
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefEnd,
    InternalRuleDefReference,
    InternalRuleType,
)

_WHITESPACE = re.compile(r"\s")


def _now_ms() -> float:
    return time.perf_counter() * 1000


class RulesBuilder:
    """Parses a GBNF grammar into a flat list of rule definitions per symbol."""

    def __init__(self, src: str, limit: float = 1000):
        self.pos = 0
        self.symbol_ids: SymbolIds = SymbolIds()
        # A sparse list, mirroring the reference's sparse array: entries that were
        # referenced but never defined stay `None`.
        self.rules: list[list[InternalRuleDef] | None] = []
        self.src = to_utf16_units(src)
        self.start = _now_ms()
        self._time_limit = limit
        self._parse(self.src)

    # ------------------------------------------------------------------ parsing

    def _at(self, pos: int) -> str:
        src = self.src
        return src[pos] if 0 <= pos < len(src) else ""

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
                    referenced = (
                        self.rules[elem.value] if elem.value < len(self.rules) else None
                    )
                    rule_exists = referenced is not None and len(referenced) > 0
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
            self._at(self.pos) == ":"
            and self._at(self.pos + 1) == ":"
            and self._at(self.pos + 2) == "="
        ):
            raise GrammarParseError(src, self.pos, f"Expecting ::= at {self.pos}")
        self.pos = parse_space(src, self.pos + 3, True)

        self.parse_alternates(name, rule_id)

        if self._at(self.pos) == "\r":
            self.pos += 2 if self._at(self.pos + 1) == "\n" else 1
        elif self._at(self.pos) == "\n":
            self.pos += 1
        elif self._at(self.pos):
            raise GrammarParseError(
                src, self.pos, f"Expecting newline or end at {self.pos}"
            )
        self.pos = parse_space(src, self.pos, True)

    # ------------------------------------------------------------------- symbols

    def get_symbol_id(self, src: str, length: int) -> int:
        next_id = self.symbol_ids.size
        key = src[:length]
        if not self.symbol_ids.has(key):
            self.symbol_ids.set(key, next_id, self.pos)
        return self.symbol_ids.get(key)

    def generate_symbol_id(self, base_name: str) -> int:
        next_id = self.symbol_ids.size
        self.symbol_ids.set(f"{base_name}_{next_id}", next_id, self.pos)
        return next_id

    def add_rule(self, rule_id: int, rule: list[InternalRuleDef]) -> None:
        if rule_id >= len(self.rules):
            self.rules.extend([None] * (rule_id + 1 - len(self.rules)))
        self.rules[rule_id] = rule

    def check_duration(self) -> None:
        if _now_ms() - self.start > self._time_limit:
            raise GrammarParseError(
                self.src, self.pos, f"duration of {self._time_limit} exceeded:"
            )

    # ----------------------------------------------------------------- sequences

    def parse_sequence(
        self,
        rule_name: str,
        out_elements: list[InternalRuleDef],
        depth: int = 0,
    ) -> None:
        is_nested = depth != 0
        src = self.src
        last_sym_start = len(out_elements)
        while self._at(self.pos):
            char = self._at(self.pos)
            if char == '"':
                self.pos += 1
                last_sym_start = len(out_elements)
                while self._at(self.pos) != '"':
                    self.check_duration()
                    value, inc_pos = parse_char(src, self.pos)
                    out_elements.append(InternalRuleDefChar([value]))
                    # Adjusting pos by the length of parsed characters
                    self.pos += inc_pos
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif char == "[":
                self.pos += 1
                start_type = InternalRuleType.CHAR
                if self._at(self.pos) == "^":
                    self.pos += 1
                    start_type = InternalRuleType.CHAR_NOT
                last_sym_start = len(out_elements)
                while self._at(self.pos) != "]":
                    self.check_duration()
                    type_ = (
                        InternalRuleType.CHAR_ALT
                        if last_sym_start < len(out_elements)
                        else start_type
                    )
                    startchar_value, inc_pos = parse_char(src, self.pos)
                    self.pos += inc_pos
                    if type_ == InternalRuleType.CHAR:
                        out_elements.append(InternalRuleDefChar([startchar_value]))
                    elif type_ == InternalRuleType.CHAR_NOT:
                        out_elements.append(InternalRuleDefCharNot([startchar_value]))
                    else:
                        out_elements.append(InternalRuleDefCharAlt(startchar_value))

                    if self._at(self.pos) == "-" and self._at(self.pos + 1) != "]":
                        self.pos += 1
                        endchar_value, inc_pos = parse_char(src, self.pos)
                        out_elements.append(
                            InternalRuleDefCharRngUpper(endchar_value)
                        )
                        self.pos += inc_pos
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif is_word_char(char):
                name = parse_name(src, self.pos)
                ref_rule_id = self.get_symbol_id(name, len(name))
                self.pos += len(name)
                self.pos = parse_space(src, self.pos, is_nested)

                last_sym_start = len(out_elements)
                out_elements.append(InternalRuleDefReference(ref_rule_id))
            elif char == "(":
                self.pos = parse_space(src, self.pos + 1, True)
                sub_rule_id = self.generate_symbol_id(rule_name)
                self.parse_alternates(rule_name, sub_rule_id, depth + 1)
                last_sym_start = len(out_elements)
                out_elements.append(InternalRuleDefReference(sub_rule_id))
                if self._at(self.pos) != ")":
                    raise GrammarParseError(src, self.pos, f"Expecting ')' at {self.pos}")
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif char in ("*", "+", "?"):
                if last_sym_start == len(out_elements):
                    raise GrammarParseError(
                        src, self.pos, f"Expecting preceding item to */+/? at {self.pos}"
                    )
                sub_rule_id = self.generate_symbol_id(rule_name)
                sub_rule: list[InternalRuleDef] = out_elements[last_sym_start:]
                if char in ("*", "+"):
                    sub_rule.append(InternalRuleDefReference(sub_rule_id))
                sub_rule.append(InternalRuleDefAlt())
                if char == "+":
                    sub_rule.extend(out_elements[last_sym_start:])
                sub_rule.append(InternalRuleDefEnd())
                self.add_rule(sub_rule_id, sub_rule)
                del out_elements[last_sym_start:]
                out_elements.append(InternalRuleDefReference(sub_rule_id))
                self.pos = parse_space(src, self.pos + 1, is_nested)
            else:
                break

    def parse_alternates(self, rule_name: str, rule_id: int, depth: int = 0) -> None:
        src = self.src
        rule: list[InternalRuleDef] = []
        self.parse_sequence(rule_name, rule, depth)
        while self._at(self.pos) == "|":
            self.check_duration()
            rule.append(InternalRuleDefAlt())
            self.pos = parse_space(src, self.pos + 1, True)
            self.parse_sequence(rule_name, rule, depth)
        rule.append(InternalRuleDefEnd())
        self.add_rule(rule_id, rule)

    # camelCase aliases, mirroring the reference API.
    symbolIds = property(lambda self: self.symbol_ids)
    getSymbolId = get_symbol_id
    generateSymbolId = generate_symbol_id
    addRule = add_rule
    checkDuration = check_duration
    parseSequence = parse_sequence
    parseAlternates = parse_alternates
