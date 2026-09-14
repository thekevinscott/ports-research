from __future__ import annotations

from enum import Enum
from typing import Union


class InternalRuleType(str, Enum):
    CHAR = "char"
    CHAR_ALT = "char_alt"
    ALT = "alt"
    CHAR_NOT = "char_not"
    CHAR_RNG_UPPER = "char_rng_upper"
    REFERENCE = "reference"
    END = "end"

    def __str__(self) -> str:
        return str(self.value)


class InternalRuleDefChar:
    def __init__(self, value: list[int] | None = None) -> None:
        self.type = InternalRuleType.CHAR
        self.value = list(value) if value is not None else []


class InternalRuleDefCharAlt:
    def __init__(self, value: int) -> None:
        self.type = InternalRuleType.CHAR_ALT
        self.value = value


class InternalRuleDefAlt:
    def __init__(self) -> None:
        self.type = InternalRuleType.ALT


class InternalRuleDefCharNot:
    def __init__(self, value: list[int] | None = None) -> None:
        self.type = InternalRuleType.CHAR_NOT
        self.value = list(value) if value is not None else []


class InternalRuleDefCharRngUpper:
    def __init__(self, value: int) -> None:
        self.type = InternalRuleType.CHAR_RNG_UPPER
        self.value = value


class InternalRuleDefReference:
    def __init__(self, value: int) -> None:
        self.type = InternalRuleType.REFERENCE
        self.value = value


class InternalRuleDefEnd:
    def __init__(self) -> None:
        self.type = InternalRuleType.END


InternalRuleDef = Union[
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefReference,
    InternalRuleDefEnd,
]

InternalRuleDefCharOrAltChar = Union[InternalRuleDefChar, InternalRuleDefCharAlt]


def is_rule_def_alt(rule: object | None = None) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule: object | None = None) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule: object | None = None) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule: object | None = None) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule: object | None = None) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule: object | None = None) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule: object | None = None) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
