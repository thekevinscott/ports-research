from enum import Enum
from typing import List, Optional, Union

from ..utils.validate_non_empty import validate_non_empty


class InternalRuleType(str, Enum):
    CHAR = "char"
    CHAR_ALT = "char_alt"
    CHAR_NOT = "char_not"
    CHAR_RNG_UPPER = "char_rng_upper"
    REF = "ref"
    ALT = "alt"
    END = "end"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class InternalBase:
    type: InternalRuleType

    def __repr__(self) -> str:
        value = getattr(self, "value", None)
        if value is None:
            return f"{type(self).__name__}()"
        return f"{type(self).__name__}({value!r})"


class InternalBaseWithInt(InternalBase):
    def __init__(self, value: int):
        self.value = value


class InternalBaseWithListOfInts(InternalBase):
    def __init__(self, value: List[int]):
        self.value = list(validate_non_empty(value))


class InternalRuleDefChar(InternalBaseWithListOfInts):
    def __init__(self, value: List[int]):
        self.type = InternalRuleType.CHAR
        super().__init__(value)


class InternalRuleDefCharNot(InternalBaseWithListOfInts):
    def __init__(self, value: List[int]):
        self.type = InternalRuleType.CHAR_NOT
        super().__init__(value)


class InternalRuleDefCharAlt(InternalBaseWithInt):
    def __init__(self, value: int):
        self.type = InternalRuleType.CHAR_ALT
        super().__init__(value)


class InternalRuleDefCharRngUpper(InternalBaseWithInt):
    def __init__(self, value: int):
        self.type = InternalRuleType.CHAR_RNG_UPPER
        super().__init__(value)


class InternalRuleDefReference(InternalBaseWithInt):
    def __init__(self, value: int):
        self.type = InternalRuleType.REF
        super().__init__(value)


class InternalRuleDefAlt(InternalBase):
    def __init__(self) -> None:
        self.type = InternalRuleType.ALT


class InternalRuleDefEnd(InternalBase):
    def __init__(self) -> None:
        self.type = InternalRuleType.END


InternalRuleDef = Union[
    InternalRuleDefChar,
    InternalRuleDefCharNot,
    InternalRuleDefCharAlt,
    InternalRuleDefCharRngUpper,
    InternalRuleDefReference,
    InternalRuleDefAlt,
    InternalRuleDefEnd,
]

InternalRuleDefCharOrAltChar = Union[InternalRuleDefChar, InternalRuleDefCharAlt]


def is_rule_def_alt(rule: Optional[InternalRuleDef] = None) -> bool:
    return getattr(rule, "type", None) == InternalRuleType.ALT


def is_rule_def_ref(rule: Optional[InternalRuleDef] = None) -> bool:
    return getattr(rule, "type", None) == InternalRuleType.REF


def is_rule_def_end(rule: Optional[InternalRuleDef] = None) -> bool:
    return getattr(rule, "type", None) == InternalRuleType.END


def is_rule_def_char(rule: Optional[InternalRuleDef] = None) -> bool:
    return getattr(rule, "type", None) == InternalRuleType.CHAR


def is_rule_def_char_not(rule: Optional[InternalRuleDef] = None) -> bool:
    return getattr(rule, "type", None) == InternalRuleType.CHAR_NOT


def is_rule_def_char_alt(rule: Optional[InternalRuleDef] = None) -> bool:
    return getattr(rule, "type", None) == InternalRuleType.CHAR_ALT


def is_rule_def_char_rng_upper(rule: Optional[InternalRuleDef] = None) -> bool:
    return getattr(rule, "type", None) == InternalRuleType.CHAR_RNG_UPPER
