from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional, Union

if TYPE_CHECKING:
    from .pointers import Pointers


class RuleType(str, Enum):
    CHAR = 'char'
    CHAR_EXCLUDE = 'char_exclude'
    END = 'end'
    REF = 'ref'


# A range is a two element list of code points, [start, end].
Range = List[int]

RuleValue = List[Union[int, Range]]

Colorize = Callable[[Union[str, int], str], str]


class PrintOpts:
    def __init__(
        self,
        colorize: Colorize,
        pointers: Optional['Pointers'] = None,
        show_position: bool = False,
    ):
        self.colorize = colorize
        self.pointers = pointers
        self.show_position = show_position


class RuleChar:
    def __init__(self, value: RuleValue):
        self.type = RuleType.CHAR
        self.value: RuleValue = list(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleChar):
            return NotImplemented
        return self.value == other.value

    def __repr__(self) -> str:
        return f'RuleChar({self.value!r})'


class RuleCharExclude:
    def __init__(self, value: RuleValue):
        self.type = RuleType.CHAR_EXCLUDE
        self.value: RuleValue = list(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleCharExclude):
            return NotImplemented
        return self.value == other.value

    def __repr__(self) -> str:
        return f'RuleCharExclude({self.value!r})'


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleEnd):
            return NotImplemented
        return True

    def __repr__(self) -> str:
        return 'RuleEnd()'


# UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
# ResolvedRule = RuleChar | RuleCharExclude | RuleEnd
# RuleRefs should never be exposed to the end user.

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]
