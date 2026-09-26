from __future__ import annotations

from enum import Enum
from typing import List, Optional


class InternalRuleType(str, Enum):
    CHAR = 'CHAR'
    CHAR_ALT = 'CHAR_ALT'
    CHAR_NOT = 'CHAR_NOT'
    CHAR_RNG_UPPER = 'CHAR_RNG_UPPER'
    ALT = 'ALT'
    END = 'END'
    RULE_REF = 'RULE_REF'


class InternalRuleDef:
    """A single element of a linear rule definition.

    `value` is a list of code points for CHAR/CHAR_NOT, a single code point for
    CHAR_ALT/CHAR_RNG_UPPER, a rule id for RULE_REF, and absent for ALT/END.
    """

    __slots__ = ('type', 'value')

    def __init__(self, type: InternalRuleType, value=None):
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        if self.value is None:
            return f'InternalRuleDef({self.type.value})'
        return f'InternalRuleDef({self.type.value}, {self.value!r})'


def internal_rule_def_char(value: List[int]) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR, value)


def internal_rule_def_char_not(value: List[int]) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_NOT, value)


def internal_rule_def_char_alt(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_ALT, value)


def internal_rule_def_char_rng_upper(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_RNG_UPPER, value)


def internal_rule_def_reference(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.RULE_REF, value)


def internal_rule_def_alt() -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.ALT)


def internal_rule_def_end() -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.END)


def is_rule_def_alt(rule: Optional[InternalRuleDef]) -> bool:
    return rule is not None and rule.type == InternalRuleType.ALT


def is_rule_def_ref(rule: Optional[InternalRuleDef]) -> bool:
    return rule is not None and rule.type == InternalRuleType.RULE_REF


def is_rule_def_end(rule: Optional[InternalRuleDef]) -> bool:
    return rule is not None and rule.type == InternalRuleType.END


def is_rule_def_char(rule: Optional[InternalRuleDef]) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR


def is_rule_def_char_not(rule: Optional[InternalRuleDef]) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_NOT


def is_rule_def_char_alt(rule: Optional[InternalRuleDef]) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_ALT


def is_rule_def_char_rng_upper(rule: Optional[InternalRuleDef]) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_RNG_UPPER
