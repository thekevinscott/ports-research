from enum import Enum
from typing import Any, List, Optional


class InternalRuleType(str, Enum):
    CHAR = "char"
    CHAR_RNG_UPPER = "char_rng_upper"
    CHAR_ALT = "char_alt"
    CHAR_NOT = "char_not"
    REF = "ref"
    ALT = "alt"
    END = "end"

    def __str__(self) -> str:
        return self.value


class InternalRuleDef:
    """A tagged rule definition; `value` is absent for `alt` and `end` rules."""

    __slots__ = ("type", "value")

    def __init__(self, type: InternalRuleType, value: Any = None):
        self.type = type
        self.value = value

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.type == other.type and self.value == other.value

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type.value!r})"
        return f"InternalRuleDef({self.type.value!r}, {self.value!r})"


def internal_rule_def_char(value: List[int]) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR, list(value))


def internal_rule_def_char_not(value: List[int]) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_NOT, list(value))


def internal_rule_def_char_alt(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_ALT, value)


def internal_rule_def_char_rng_upper(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_RNG_UPPER, value)


def internal_rule_def_reference(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.REF, value)


def internal_rule_def_alt() -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.ALT)


def internal_rule_def_end() -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.END)


def _type_of(rule: Any) -> Optional[InternalRuleType]:
    return getattr(rule, "type", None)


def is_rule_def_alt(rule: Any = None) -> bool:
    return _type_of(rule) == InternalRuleType.ALT


def is_rule_def_ref(rule: Any = None) -> bool:
    return _type_of(rule) == InternalRuleType.REF


def is_rule_def_end(rule: Any = None) -> bool:
    return _type_of(rule) == InternalRuleType.END


def is_rule_def_char(rule: Any = None) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR


def is_rule_def_char_not(rule: Any = None) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_NOT


def is_rule_def_char_alt(rule: Any = None) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_ALT


def is_rule_def_char_rng_upper(rule: Any = None) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_RNG_UPPER
