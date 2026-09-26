from enum import Enum
from typing import List, Union

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]

# a Range is a two element list of code points, inclusive on both ends.
Range = List[int]


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:
        return str(self.value)


class Rule:
    """Base class for the rules handed back to the caller."""

    type: RuleType

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(repr(self.__dict__))


class RuleChar(Rule):
    def __init__(self, value: List[Union[int, Range]]):
        self.type = RuleType.CHAR
        self.value = value

    def __repr__(self) -> str:
        return f"RuleChar({self.value!r})"


class RuleCharExclude(Rule):
    def __init__(self, value: List[Union[int, Range]]):
        self.type = RuleType.CHAR_EXCLUDE
        self.value = value

    def __repr__(self) -> str:
        return f"RuleCharExclude({self.value!r})"


class RuleEnd(Rule):
    def __init__(self) -> None:
        self.type = RuleType.END

    def __repr__(self) -> str:
        return "RuleEnd()"
