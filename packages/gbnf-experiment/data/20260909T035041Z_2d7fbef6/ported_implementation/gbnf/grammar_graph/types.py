from __future__ import annotations

from enum import Enum
from typing import List, Sequence, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


Range = List[int]


def _json_value(value) -> str:
    """Serialize a rule value the way ``JSON.stringify`` would."""
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_json_value(item) for item in value) + "]"
    if isinstance(value, float) and value != value:  # NaN
        return "null"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


class Rule:
    """Base class for the rules exposed to consumers of a :class:`ParseState`."""

    __slots__ = ()

    type: RuleType

    def to_json(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return NotImplemented
        return self.to_json() == other.to_json()

    def __hash__(self) -> int:
        return hash(self.to_json())

    def __repr__(self) -> str:
        return self.to_json()


class RuleChar(Rule):
    __slots__ = ("value",)
    type = RuleType.CHAR

    def __init__(self, value: Sequence[Union[int, Range]]):
        self.value: list[Union[int, Range]] = list(value)

    def to_json(self) -> str:
        return f'{{"type":"{self.type.value}","value":{_json_value(self.value)}}}'


class RuleCharExclude(Rule):
    __slots__ = ("value",)
    type = RuleType.CHAR_EXCLUDE

    def __init__(self, value: Sequence[Union[int, Range]]):
        self.value: list[Union[int, Range]] = list(value)

    def to_json(self) -> str:
        return f'{{"type":"{self.type.value}","value":{_json_value(self.value)}}}'


class RuleEnd(Rule):
    __slots__ = ()
    type = RuleType.END

    def to_json(self) -> str:
        return f'{{"type":"{self.type.value}"}}'


# UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
# RuleRefs should never be exposed to the end user, so:
# ResolvedRule = RuleCharExclude | RuleChar | RuleEnd

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]
