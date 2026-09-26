from enum import Enum
from typing import Dict, List, Optional, Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"
    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"


class InternalRuleDef:
    """A single element of a linear (not yet stacked) rule definition.

    Mirrors the discriminated union in the reference: `value` is a list of code
    points for CHAR/CHAR_NOT, a single code point for CHAR_ALT/CHAR_RNG_UPPER, a
    rule id for RULE_REF, and unused for ALT/END.
    """

    __slots__ = ("type", "value")

    def __init__(
        self,
        type: InternalRuleType,
        value: Union[List[int], int, None] = None,
    ):
        self.type = type
        self.value = value

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, InternalRuleDef)
            and self.type == other.type
            and self.value == other.value
        )

    def __hash__(self) -> int:
        value = tuple(self.value) if isinstance(self.value, list) else self.value
        return hash((self.type, value))

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type.value})"
        return f"InternalRuleDef({self.type.value}, {self.value!r})"


def internal_rule_def_char(value: List[int]) -> InternalRuleDef:
    # the reference copies the incoming list so that later mutation of the
    # source list cannot leak into the rule.
    return InternalRuleDef(InternalRuleType.CHAR, list(value))


def internal_rule_def_char_not(value: List[int]) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_NOT, list(value))


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


def _is(rule: Optional[InternalRuleDef], type: InternalRuleType) -> bool:
    return rule is not None and rule.type == type


def is_rule_def_alt(rule: Optional[InternalRuleDef]) -> bool:
    return _is(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule: Optional[InternalRuleDef]) -> bool:
    return _is(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule: Optional[InternalRuleDef]) -> bool:
    return _is(rule, InternalRuleType.END)


def is_rule_def_char(rule: Optional[InternalRuleDef]) -> bool:
    return _is(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule: Optional[InternalRuleDef]) -> bool:
    return _is(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule: Optional[InternalRuleDef]) -> bool:
    return _is(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule: Optional[InternalRuleDef]) -> bool:
    return _is(rule, InternalRuleType.CHAR_RNG_UPPER)


SymbolIdsMap = Dict[str, int]
