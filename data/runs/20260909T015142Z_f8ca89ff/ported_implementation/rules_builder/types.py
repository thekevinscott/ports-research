from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Mapping, Sequence

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
]


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:
        return self.value


class InternalRuleDef:
    """`{ type, value? }` as produced by the rules builder."""

    __slots__ = ("type", "value")

    def __init__(self, type: InternalRuleType, value: Any = None):
        self.type = type
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        if self.value is None:
            return {"type": self.type.value}
        value = list(self.value) if isinstance(self.value, (list, tuple)) else self.value
        return {"type": self.type.value, "value": value}

    def keys(self):
        return self.to_dict().keys()

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, InternalRuleDef):
            return self.to_dict() == other.to_dict()
        if isinstance(other, Mapping):
            return self.to_dict() == dict(other)
        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self) -> int:
        value = self.value
        if isinstance(value, (list, tuple)):
            value = tuple(value)
        return hash((self.type, value))

    def __repr__(self) -> str:
        if self.value is None:
            return f"{{type: {self.type.value}}}"
        return f"{{type: {self.type.value}, value: {self.value!r}}}"


def InternalRuleDefChar(value: Sequence[int]) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR, list(value))


def InternalRuleDefCharNot(value: Sequence[int]) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_NOT, list(value))


def InternalRuleDefCharAlt(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_ALT, value)


def InternalRuleDefCharRngUpper(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.CHAR_RNG_UPPER, value)


def InternalRuleDefReference(value: int) -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.RULE_REF, value)


def InternalRuleDefAlt() -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.ALT)


def InternalRuleDefEnd() -> InternalRuleDef:
    return InternalRuleDef(InternalRuleType.END)
