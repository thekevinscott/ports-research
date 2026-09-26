from typing import Callable, List, Union

from ..utils.validate_non_empty import validate_non_empty
from .rule_type import RuleType

Colorize = Callable[[Union[str, int]], str]

# A range is a two element list of code points, `[start, end]`.
Range = List[int]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


class RuleChar:
    def __init__(self, value: List[Union[int, Range]]):
        self.type = RuleType.CHAR
        self.value = validate_non_empty(list(value))

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.value == other.value

    def __repr__(self) -> str:
        return f"RuleChar({self.value!r})"


class RuleCharExclude:
    def __init__(self, value: List[Union[int, Range]]):
        self.type = RuleType.CHAR_EXCLUDE
        self.value = validate_non_empty(list(value))

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.value == other.value

    def __repr__(self) -> str:
        return f"RuleCharExclude({self.value!r})"


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return True

    def __repr__(self) -> str:
        return "RuleEnd()"


def rule_char(value: List[Union[int, Range]]) -> RuleChar:
    return RuleChar(value)


def rule_char_exclude(value: List[Union[int, Range]]) -> RuleCharExclude:
    return RuleCharExclude(value)


def rule_end() -> RuleEnd:
    return RuleEnd()
