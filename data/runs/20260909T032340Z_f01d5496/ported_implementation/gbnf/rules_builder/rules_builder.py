import re
import time
from typing import Dict, List, Optional

from ..utils.errors.grammar_parse_error import GrammarParseError
from .is_word_char import is_word_char
from .parse_char import parse_char
from .parse_name import parse_name
from .parse_space import parse_space
from .symbol_ids import SymbolIds
from .types import InternalRuleDef, InternalRuleType

_WHITESPACE = re.compile(r"\s")


class RulesBuilder:
    def __init__(self, src: str, limit: int = 1000):
        self.pos = 0
        self.symbol_ids = SymbolIds()
        # rules are assigned by id, and ids are not necessarily assigned in order, so
        # they're collected in a map and flattened out into a (possibly sparse) list.
        self._rules_by_id: Dict[int, List[InternalRuleDef]] = {}
        self.src = src
        self.start = time.perf_counter() * 1000
        self._time_limit = limit
        self.parse(src)

    @property
    def rules(self) -> List[Optional[List[InternalRuleDef]]]:
        if not self._rules_by_id:
            return []
        length = max(self._rules_by_id) + 1
        return [self._rules_by_id.get(idx) for idx in range(length)]

    def _at(self, pos: int):
        return self.src[pos] if 0 <= pos < len(self.src) else None

    def parse(self, src: str) -> None:
        # move cursor forward until we reach non-whitespace content
        self.pos = parse_space(src, 0, True)

        while self.pos < len(src):
            self.parse_rule(src)

        # Validate the state to ensure that all rules are defined
        for rule in self.rules:
            if rule is None:
                continue
            for elem in rule:
                if elem.type == InternalRuleType.RULE_REF:
                    # Ensure that the rule at that location exists
                    referenced = self._rules_by_id.get(elem.value)
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

    def parse_rule(self, src: str) -> None:
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

    def add_rule(self, rule_id: int, rule: List[InternalRuleDef]) -> None:
        self._rules_by_id[rule_id] = rule

    def check_duration(self) -> None:
        if time.perf_counter() * 1000 - self.start > self._time_limit:
            raise GrammarParseError(
                self.src, self.pos, f"duration of {self._time_limit} exceeded:"
            )

    def parse_sequence(
        self,
        rule_name: str,
        out_elements: List[InternalRuleDef],
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
                    out_elements.append(
                        InternalRuleDef(InternalRuleType.CHAR, [value])
                    )
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
                    if type_ in (InternalRuleType.CHAR, InternalRuleType.CHAR_NOT):
                        out_elements.append(
                            InternalRuleDef(type_, [startchar_value])
                        )
                    else:
                        out_elements.append(
                            InternalRuleDef(type_, startchar_value)
                        )

                    if self._at(self.pos) == "-" and self._at(self.pos + 1) != "]":
                        self.pos += 1
                        endchar_value, inc_pos = parse_char(src, self.pos)
                        out_elements.append(
                            InternalRuleDef(
                                InternalRuleType.CHAR_RNG_UPPER, endchar_value
                            )
                        )
                        self.pos += inc_pos
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif is_word_char(char):
                name = parse_name(src, self.pos)
                ref_rule_id = self.get_symbol_id(name, len(name))
                self.pos += len(name)
                self.pos = parse_space(src, self.pos, is_nested)

                last_sym_start = len(out_elements)
                out_elements.append(
                    InternalRuleDef(InternalRuleType.RULE_REF, ref_rule_id)
                )
            elif char == "(":
                self.pos = parse_space(src, self.pos + 1, True)
                sub_rule_id = self.generate_symbol_id(rule_name)
                self.parse_alternates(rule_name, sub_rule_id, depth + 1)
                last_sym_start = len(out_elements)
                out_elements.append(
                    InternalRuleDef(InternalRuleType.RULE_REF, sub_rule_id)
                )
                if self._at(self.pos) != ")":
                    raise GrammarParseError(
                        src, self.pos, f"Expecting ')' at {self.pos}"
                    )
                self.pos = parse_space(src, self.pos + 1, is_nested)
            elif char in ("*", "+", "?"):
                if last_sym_start == len(out_elements):
                    raise GrammarParseError(
                        src,
                        self.pos,
                        f"Expecting preceding item to */+/? at {self.pos}",
                    )
                sub_rule_id = self.generate_symbol_id(rule_name)
                sub_rule: List[InternalRuleDef] = out_elements[last_sym_start:]
                if char in ("*", "+"):
                    sub_rule.append(
                        InternalRuleDef(InternalRuleType.RULE_REF, sub_rule_id)
                    )
                sub_rule.append(InternalRuleDef(InternalRuleType.ALT))
                if char == "+":
                    sub_rule.extend(out_elements[last_sym_start:])
                sub_rule.append(InternalRuleDef(InternalRuleType.END))
                self.add_rule(sub_rule_id, sub_rule)
                del out_elements[last_sym_start:]
                out_elements.append(
                    InternalRuleDef(InternalRuleType.RULE_REF, sub_rule_id)
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
        rule: List[InternalRuleDef] = []
        self.parse_sequence(rule_name, rule, depth)
        while self._at(self.pos) == "|":
            self.check_duration()
            rule.append(InternalRuleDef(InternalRuleType.ALT))
            self.pos = parse_space(src, self.pos + 1, True)
            self.parse_sequence(rule_name, rule, depth)
        rule.append(InternalRuleDef(InternalRuleType.END))
        self.add_rule(rule_id, rule)
