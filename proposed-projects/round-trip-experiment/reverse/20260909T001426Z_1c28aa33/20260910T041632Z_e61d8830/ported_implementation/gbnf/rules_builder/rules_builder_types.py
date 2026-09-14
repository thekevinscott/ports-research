from enum import Enum
from typing import List, Optional, Sequence


class InternalRuleType(str, Enum):
    CHAR = "char"
    CHAR_ALT = "char_alt"
    ALT = "alt"
    CHAR_NOT = "char_not"
    CHAR_RNG_UPPER = "char_rng_upper"
    REF = "ref"
    END = "end"


class InternalBase:
    type: InternalRuleType

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class InternalBaseWithInt(InternalBase):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class InternalBaseWithListOfInts(InternalBase):
    def __init__(self, value: Sequence[int]):
        # the incoming list is copied so later mutations of the source do not leak in.
        self.value: List[int] = list(value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class InternalRuleDefChar(InternalBaseWithListOfInts):
    type = InternalRuleType.CHAR


class InternalRuleDefCharNot(InternalBaseWithListOfInts):
    type = InternalRuleType.CHAR_NOT


class InternalRuleDefCharAlt(InternalBaseWithInt):
    type = InternalRuleType.CHAR_ALT


class InternalRuleDefCharRngUpper(InternalBaseWithInt):
    type = InternalRuleType.CHAR_RNG_UPPER


class InternalRuleDefReference(InternalBaseWithInt):
    type = InternalRuleType.REF


class InternalRuleDefAlt(InternalBase):
    type = InternalRuleType.ALT


class InternalRuleDefEnd(InternalBase):
    type = InternalRuleType.END


InternalRuleDef = InternalBase


def is_rule_def_alt(rule: Optional[InternalRuleDef]) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule: Optional[InternalRuleDef]) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule: Optional[InternalRuleDef]) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule: Optional[InternalRuleDef]) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule: Optional[InternalRuleDef]) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule: Optional[InternalRuleDef]) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule: Optional[InternalRuleDef]) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
