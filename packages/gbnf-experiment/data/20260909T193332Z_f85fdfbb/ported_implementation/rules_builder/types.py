from __future__ import annotations

from enum import StrEnum
from typing import Union


class InternalRuleType(StrEnum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"


class InternalRuleDef:
    """Base class for the flat rule definitions produced by ``RulesBuilder``."""

    __slots__ = ()
    type: InternalRuleType

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"{type(self).__name__}({self.to_dict()})"

    def to_dict(self) -> dict:
        return {"type": str(self.type)}

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InternalRuleDef):
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == other
        return NotImplemented

    def __hash__(self) -> int:
        values = self.to_dict().get("value")
        if isinstance(values, list):
            values = tuple(values)
        return hash((self.type, values))


class _ValueRuleDef(InternalRuleDef):
    __slots__ = ("value",)

    def to_dict(self) -> dict:
        value = self.value
        return {"type": str(self.type), "value": list(value) if isinstance(value, list) else value}


class InternalRuleDefChar(_ValueRuleDef):
    """A literal character, or the first character of a bracket expression."""

    __slots__ = ()
    type = InternalRuleType.CHAR

    def __init__(self, value: list[int]):
        self.value = list(value)


class InternalRuleDefCharNot(_ValueRuleDef):
    """The first character of a negated bracket expression."""

    __slots__ = ()
    type = InternalRuleType.CHAR_NOT

    def __init__(self, value: list[int]):
        self.value = list(value)


class InternalRuleDefCharAlt(_ValueRuleDef):
    """An additional alternative inside a bracket expression."""

    __slots__ = ()
    type = InternalRuleType.CHAR_ALT

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefCharRngUpper(_ValueRuleDef):
    """The upper bound of an ``a-z`` style range."""

    __slots__ = ()
    type = InternalRuleType.CHAR_RNG_UPPER

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefReference(_ValueRuleDef):
    """A reference to another rule, by symbol id."""

    __slots__ = ()
    type = InternalRuleType.RULE_REF

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefAlt(InternalRuleDef):
    """Separates alternatives within a rule."""

    __slots__ = ()
    type = InternalRuleType.ALT


class InternalRuleDefEnd(InternalRuleDef):
    """Terminates a rule."""

    __slots__ = ()
    type = InternalRuleType.END


InternalRuleDefWithNumericValue = Union[
    InternalRuleDefReference, InternalRuleDefCharAlt, InternalRuleDefCharRngUpper
]
InternalRuleDefWithoutValue = Union[InternalRuleDefAlt, InternalRuleDefEnd]
InternalRuleDefCharOrAltChar = Union[InternalRuleDefChar, InternalRuleDefCharAlt]

__all__ = [
    "InternalRuleType",
    "InternalRuleDef",
    "InternalRuleDefChar",
    "InternalRuleDefCharNot",
    "InternalRuleDefCharAlt",
    "InternalRuleDefCharRngUpper",
    "InternalRuleDefReference",
    "InternalRuleDefAlt",
    "InternalRuleDefEnd",
    "InternalRuleDefWithNumericValue",
    "InternalRuleDefWithoutValue",
    "InternalRuleDefCharOrAltChar",
]
