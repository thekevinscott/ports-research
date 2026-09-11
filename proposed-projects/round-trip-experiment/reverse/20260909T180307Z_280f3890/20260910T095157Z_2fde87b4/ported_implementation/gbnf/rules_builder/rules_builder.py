import time
from typing import List, Optional

from ..utils.errors import GrammarParseError
from .is_word_char import is_word_char
from .parse_char import parse_char
from .parse_name import parse_name
from .parse_space import parse_space
from .rules_builder_types import (
    InternalRuleDefAlt,
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefEnd,
    InternalRuleDefReference,
    InternalRuleType,
)
from .symbol_ids import SymbolIds

# The characters JavaScript's `\s` matches, since the reference implementation
# uses a regex to skip whitespace when reporting an undefined rule.
_JS_WHITESPACE = frozenset(
    "\f\n\r\t\v            "
    "      　﻿"
)


def _char_at(src: str, pos: int) -> Optional[str]:
    """Index `src` the way JavaScript does — out of bounds yields nothing."""
    if 0 <= pos < len(src):
        return src[pos]
    return None


def get_out_elements(type_of_rule: str, startchar_value: int):
    if type_of_rule == InternalRuleType.CHAR:
        return InternalRuleDefChar([startchar_value])
    if type_of_rule == InternalRuleType.CHAR_NOT:
        return InternalRuleDefCharNot([startchar_value])
    if type_of_rule == InternalRuleType.CHAR_RNG_UPPER:
        return InternalRuleDefCharRngUpper(startchar_value)
    if type_of_rule == InternalRuleType.ALT:
        return InternalRuleDefAlt()
    if type_of_rule == InternalRuleType.END:
        return InternalRuleDefEnd()
    if type_of_rule == InternalRuleType.CHAR_ALT:
        return InternalRuleDefCharAlt(startchar_value)
    raise Exception(f"Invalid type: {type_of_rule}")


class RulesBuilder:
    def __init__(self, src: str, limit: int = 1000):
        self.pos = 0
        self.symbol_ids = SymbolIds()
        self.rules: List[List[object]] = []
        self.src = src
        self.start = time.time()
        self.time_limit = limit
        self.parse(src)

    def parse(self, src: str) -> None:
        self.pos = parse_space(src, 0, True)
        while self.pos < len(src):
            self.parse_rule(src)

        # Validate the state to ensure that all rules are defined
        for rule in self.rules:
            for elem in rule:
                if elem.type == InternalRuleType.REFERENCE:
                    referenced = (
                        self.rules[elem.value] if 0 <= elem.value < len(self.rules) else None
                    )
                    rule_exists = referenced is not None and len(referenced) > 0
                    if not rule_exists:
                        missing_rule_name = self.symbol_ids.reverse_get(elem.value)
                        missing_rule_pos = self.symbol_ids.get_pos(missing_rule_name)

                        # Skip over the ::= and any whitespace
                        while missing_rule_pos < len(src) and (
                            src[missing_rule_pos] == ":"
                            or src[missing_rule_pos] == "="
                            or src[missing_rule_pos] in _JS_WHITESPACE
                        ):
                            missing_rule_pos += 1

                        raise GrammarParseError(
                            src,
                            missing_rule_pos,
                            f'Undefined rule identifier "{missing_rule_name}"',
                        )

    def parse_rule(self, src: str) -> None:
        name = parse_name(src, self.pos)
        self.pos = parse_space(src, self.pos + len(name), False)
        rule_id = self.get_symbol_id(name, len(name))

        self.pos = parse_space(src, self.pos, True)
        if not (
            self.pos + 2 < len(src)  # Ensure the position + 2 is within bounds
            and src[self.pos] == ":"
            and src[self.pos + 1] == ":"
            and src[self.pos + 2] == "="
        ):
            raise GrammarParseError(src, self.pos, f"Expecting ::= at {self.pos}")
        self.pos += 3
        self.pos = parse_space(src, self.pos, True)

        self.parse_alternates(name, rule_id)

        # Check if self.pos is within the bounds of src before checking for a carriage return
        if self.pos < len(src) and src[self.pos] == "\r":
            self.pos += 2 if _char_at(src, self.pos + 1) == "\n" else 1
        elif self.pos < len(src) and src[self.pos] == "\n":
            self.pos += 1
        elif self.pos < len(src) and src[self.pos]:
            raise GrammarParseError(
                src, self.pos, f"Expecting newline or end at {self.pos}"
            )
        self.pos = parse_space(src, self.pos, True)

    def get_symbol_id(self, src: str, length: int) -> int:
        next_id = self.symbol_ids.size
        key = src[0:length]
        if not self.symbol_ids.has(key):
            self.symbol_ids.set(key, next_id, self.pos)
        return self.symbol_ids.get(key)

    def generate_symbol_id(self, base_name: str) -> int:
        next_id = self.symbol_ids.size
        self.symbol_ids.set(f"{base_name}_{next_id}", next_id, self.pos)
        return next_id

    def add_rule(self, rule_id: int, rule: List[object]) -> None:
        while len(self.rules) <= rule_id:
            self.rules.append([])
        self.rules[rule_id] = rule

    def check_duration(self) -> None:
        if time.time() - self.start > self.time_limit:
            raise GrammarParseError(
                self.src, self.pos, f"Duration of {self.time_limit} exceeded"
            )

    def parse_sequence(
        self, rule_name: str, out_elements: List[object], depth: int = 0
    ) -> None:
        is_nested = depth != 0
        src = self.src
        last_sym_start = len(out_elements)

        while self.pos < len(src):
            if src[self.pos] == '"':
                self.pos += 1
                last_sym_start = len(out_elements)
                while _char_at(src, self.pos) != '"':
                    self.check_duration()
                    value, inc_pos = parse_char(src, self.pos)
                    out_elements.append(InternalRuleDefChar([value]))
                    self.pos += inc_pos
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif src[self.pos] == "[":
                self.pos += 1
                start_type = InternalRuleType.CHAR
                if _char_at(src, self.pos) == "^":
                    self.pos += 1
                    start_type = InternalRuleType.CHAR_NOT
                last_sym_start = len(out_elements)
                while _char_at(src, self.pos) != "]":
                    self.check_duration()
                    type_of_rule = (
                        InternalRuleType.CHAR_ALT
                        if last_sym_start < len(out_elements)
                        else start_type
                    )
                    startchar_value, inc_pos = parse_char(src, self.pos)
                    self.pos += inc_pos
                    out_elements.append(get_out_elements(type_of_rule, startchar_value))

                    if (
                        _char_at(src, self.pos) == "-"
                        and _char_at(src, self.pos + 1) != "]"
                    ):
                        self.pos += 1
                        endchar_value, end_inc_pos = parse_char(src, self.pos)
                        out_elements.append(InternalRuleDefCharRngUpper(endchar_value))
                        self.pos += end_inc_pos
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif is_word_char(src[self.pos]):
                name = parse_name(src, self.pos)
                ref_rule_id = self.get_symbol_id(name, len(name))
                self.pos += len(name)
                self.pos = parse_space(src, self.pos, is_nested)

                last_sym_start = len(out_elements)
                out_elements.append(InternalRuleDefReference(ref_rule_id))
            elif src[self.pos] == "(":
                self.pos = parse_space(src, self.pos + 1, True)
                sub_rule_id = self.generate_symbol_id(rule_name)
                self.parse_alternates(rule_name, sub_rule_id, depth + 1)
                last_sym_start = len(out_elements)
                out_elements.append(InternalRuleDefReference(sub_rule_id))
                if _char_at(src, self.pos) != ")":
                    raise GrammarParseError(
                        src, self.pos, f"Expecting ')' at {self.pos}"
                    )
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif src[self.pos] == "*" or src[self.pos] == "+" or src[self.pos] == "?":
                if last_sym_start == len(out_elements):
                    raise GrammarParseError(
                        src,
                        self.pos,
                        f"Expecting preceding item to */+/? at {self.pos}",
                    )
                sub_rule_id = self.generate_symbol_id(rule_name)
                sub_rule = out_elements[last_sym_start:]
                if src[self.pos] == "*" or src[self.pos] == "+":
                    sub_rule.append(InternalRuleDefReference(sub_rule_id))
                sub_rule.append(InternalRuleDefAlt())
                if src[self.pos] == "+":
                    sub_rule.extend(out_elements[last_sym_start:])
                sub_rule.append(InternalRuleDefEnd())
                self.add_rule(sub_rule_id, sub_rule)
                out_elements[last_sym_start:] = [InternalRuleDefReference(sub_rule_id)]
                self.pos = parse_space(src, self.pos + 1, is_nested)
            else:
                break

    def parse_alternates(self, rule_name: str, rule_id: int, depth: int = 0) -> None:
        src = self.src
        rule: List[object] = []
        self.parse_sequence(rule_name, rule, depth)
        # Ensure that self.pos is within bounds before checking src[self.pos]
        while self.pos < len(src) and src[self.pos] == "|":
            self.check_duration()
            rule.append(InternalRuleDefAlt())
            self.pos = parse_space(src, self.pos + 1, True)
            self.parse_sequence(rule_name, rule, depth)
        rule.append(InternalRuleDefEnd())
        self.add_rule(rule_id, rule)
