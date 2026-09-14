from __future__ import annotations

import json
from enum import StrEnum
from typing import Sequence, Union


class RuleType(StrEnum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"


Range = list  # [number, number]


class Rule:
    """Base class for the rules exposed to callers."""

    __slots__ = ()
    type: RuleType

    def to_dict(self) -> dict:
        return {"type": str(self.type)}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))

    def __getitem__(self, key: str):
        try:
            return self.to_dict()[key]
        except KeyError:
            raise KeyError(key) from None

    def __contains__(self, key: str) -> bool:
        return key in self.to_dict()

    def keys(self):
        return self.to_dict().keys()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.to_dict()})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rule):
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.to_json())


def _normalize(value: Sequence) -> list:
    """Ranges are two element lists; everything else is a bare code point."""
    return [list(v) if isinstance(v, (list, tuple)) else v for v in value]


class RuleChar(Rule):
    """One or more code points (or ranges) that the next character may match."""

    __slots__ = ("value",)
    type = RuleType.CHAR

    def __init__(self, value: Sequence):
        self.value = _normalize(value)

    def to_dict(self) -> dict:
        return {"type": str(self.type), "value": self.value}


class RuleCharExclude(Rule):
    """One or more code points (or ranges) that the next character may not match."""

    __slots__ = ("value",)
    type = RuleType.CHAR_EXCLUDE

    def __init__(self, value: Sequence):
        self.value = _normalize(value)

    def to_dict(self) -> dict:
        return {"type": str(self.type), "value": self.value}


class RuleEnd(Rule):
    """Denotes a valid end of a string."""

    __slots__ = ()
    type = RuleType.END


# RuleRefs should never be exposed to the end user.
UnresolvedRule = Union[RuleChar, RuleCharExclude, "RuleRef", RuleEnd]
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, Sequence[int]]

__all__ = [
    "RuleType",
    "Range",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "UnresolvedRule",
    "ResolvedRule",
    "ValidInput",
]
