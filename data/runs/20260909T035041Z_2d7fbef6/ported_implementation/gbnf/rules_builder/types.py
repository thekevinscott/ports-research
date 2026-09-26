from __future__ import annotations

from enum import Enum
from typing import Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


class InternalRuleDef:
    """Base class for the flat rule definitions emitted by ``RulesBuilder``."""

    __slots__ = ()

    type: InternalRuleType

    def __repr__(self) -> str:
        value = getattr(self, "value", None)
        if value is None:
            return f"{{type: {self.type.value}}}"
        return f"{{type: {self.type.value}, value: {value}}}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InternalRuleDef):
            return NotImplemented
        return self.type == other.type and getattr(self, "value", None) == getattr(
            other, "value", None
        )

    def __hash__(self) -> int:
        value = getattr(self, "value", None)
        if isinstance(value, list):
            value = tuple(value)
        return hash((self.type, value))


class InternalRuleDefChar(InternalRuleDef):
    __slots__ = ("value",)
    type = InternalRuleType.CHAR

    def __init__(self, value: list[int]):
        self.value = list(value)


class InternalRuleDefCharNot(InternalRuleDef):
    __slots__ = ("value",)
    type = InternalRuleType.CHAR_NOT

    def __init__(self, value: list[int]):
        self.value = list(value)


class InternalRuleDefCharAlt(InternalRuleDef):
    __slots__ = ("value",)
    type = InternalRuleType.CHAR_ALT

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefCharRngUpper(InternalRuleDef):
    __slots__ = ("value",)
    type = InternalRuleType.CHAR_RNG_UPPER

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefReference(InternalRuleDef):
    __slots__ = ("value",)
    type = InternalRuleType.RULE_REF

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefAlt(InternalRuleDef):
    __slots__ = ()
    type = InternalRuleType.ALT


class InternalRuleDefEnd(InternalRuleDef):
    __slots__ = ()
    type = InternalRuleType.END


InternalRuleDefCharOrAltChar = Union[InternalRuleDefChar, InternalRuleDefCharAlt]


def make_internal_rule_def(type: InternalRuleType, value=None) -> InternalRuleDef:
    """Build an ``InternalRuleDef`` from a type (mirrors JS object literals)."""
    if type is InternalRuleType.CHAR:
        return InternalRuleDefChar(value)
    if type is InternalRuleType.CHAR_NOT:
        return InternalRuleDefCharNot(value)
    if type is InternalRuleType.CHAR_ALT:
        return InternalRuleDefCharAlt(value)
    if type is InternalRuleType.CHAR_RNG_UPPER:
        return InternalRuleDefCharRngUpper(value)
    if type is InternalRuleType.RULE_REF:
        return InternalRuleDefReference(value)
    if type is InternalRuleType.ALT:
        return InternalRuleDefAlt()
    if type is InternalRuleType.END:
        return InternalRuleDefEnd()
    raise ValueError(f"Unknown internal rule type: {type}")
