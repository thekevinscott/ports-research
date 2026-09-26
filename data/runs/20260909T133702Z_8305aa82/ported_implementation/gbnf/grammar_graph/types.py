"""Rule types exposed by the parser, and the union types built on top of them."""

from enum import Enum
from typing import List, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:
        return self.value


# A range is a two element list of code points, inclusive on both ends.
Range = List[int]


class _Rule:
    """Base class providing the value semantics the reference objects rely on."""

    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Rule):
            return NotImplemented
        return type(self) is type(other) and self.__dict__ == other.__dict__

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__dict__!r})"


class RuleChar(_Rule):
    def __init__(self, value):
        self.type = RuleType.CHAR.value
        self.value = list(value)


class RuleCharExclude(_Rule):
    def __init__(self, value):
        self.type = RuleType.CHAR_EXCLUDE.value
        self.value = list(value)


class RuleEnd(_Rule):
    def __init__(self):
        self.type = RuleType.END.value


# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]
