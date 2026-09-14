from enum import Enum
from typing import Union

# A range of code points, as a two element [start, end] list.
Range = list[int]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, list[int]]


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"


class RuleChar:
    def __init__(self, value: list[Union[int, Range]]):
        self.type = RuleType.CHAR
        self.value: list[Union[int, Range]] = [*value]

    def __eq__(self, other: object) -> bool:
        if type(other) is not RuleChar:
            return NotImplemented
        return self.value == other.value

    # Rules are held in identity keyed collections while walking the graph, so
    # hashing stays identity based even though equality is by value.
    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleChar({self.value!r})"


class RuleCharExclude:
    def __init__(self, value: list[Union[int, Range]]):
        self.type = RuleType.CHAR_EXCLUDE
        self.value: list[Union[int, Range]] = [*value]

    def __eq__(self, other: object) -> bool:
        if type(other) is not RuleCharExclude:
            return NotImplemented
        return self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleCharExclude({self.value!r})"


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if type(other) is not RuleEnd:
            return NotImplemented
        return True

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return "RuleEnd()"


class PrintOpts:
    def __init__(self, colorize, pointers=None, show_position: bool = False):
        self.colorize = colorize
        self.pointers = pointers
        self.show_position = show_position
