from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Union


class RuleType(StrEnum):
    CHAR = 'char'
    CHAR_EXCLUDE = 'char_exclude'
    END = 'end'


# A [start, end] pair of code points, inclusive on both ends.
Range = list[int]


class Rule:
    """Base class for the rules handed back to callers.

    Rules compare by value (against other rules and against plain mappings,
    which keeps assertions readable) but hash by identity, because the graph
    de-duplicates rules by reference and then uses that reference as a map key
    — exactly as the reference implementation does with object identity.
    """

    type: RuleType

    __hash__ = object.__hash__

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def keys(self):
        return self.to_dict().keys()

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, Rule):
            return self.to_dict() == other.to_dict()
        if isinstance(other, Mapping):
            return self.to_dict() == dict(other)
        return NotImplemented

    def __repr__(self) -> str:
        parts = ', '.join(f'{key}={value!r}' for key, value in self.to_dict().items())
        return f'{type(self).__name__}({parts})'


class RuleChar(Rule):
    def __init__(self, value: list[int | float | Range]):
        self.type = RuleType.CHAR
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        return {'type': self.type, 'value': self.value}


class RuleCharExclude(Rule):
    def __init__(self, value: list[int | float | Range]):
        self.type = RuleType.CHAR_EXCLUDE
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        return {'type': self.type, 'value': self.value}


class RuleEnd(Rule):
    def __init__(self) -> None:
        self.type = RuleType.END

    def to_dict(self) -> dict[str, Any]:
        return {'type': self.type}


# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, list[int]]
