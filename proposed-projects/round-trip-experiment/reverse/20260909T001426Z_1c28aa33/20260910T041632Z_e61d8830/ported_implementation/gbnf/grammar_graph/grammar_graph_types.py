from enum import Enum
from typing import List, Sequence, Union

from .rule_ref import RuleRef

# A range is a two element list of code points, inclusive on both ends.
Range = List[int]


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"


class Rule:
    type: RuleType

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return getattr(self, "value", None) == getattr(other, "value", None)

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class RuleWithListOfIntsOrRanges(Rule):
    def __init__(self, value: Sequence[Union[int, Range]]):
        # copied so that mutating this rule's value never reaches back into the source list.
        self.value: List[Union[int, Range]] = list(value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class RuleChar(RuleWithListOfIntsOrRanges):
    type = RuleType.CHAR


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd(Rule):
    type = RuleType.END


# UnresolvedRule is a RuleChar, RuleCharExclude, RuleRef or RuleEnd.
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

__all__ = [
    "Range",
    "ResolvedRule",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleRef",
    "RuleType",
    "RuleWithListOfIntsOrRanges",
    "UnresolvedRule",
    "ValidInput",
]
