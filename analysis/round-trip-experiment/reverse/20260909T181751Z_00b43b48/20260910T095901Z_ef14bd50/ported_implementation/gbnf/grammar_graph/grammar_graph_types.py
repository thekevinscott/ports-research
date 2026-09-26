from typing import TYPE_CHECKING, Callable, List, Union

from ..utils.validate_non_empty import validate_non_empty
from .rule_ref import RuleRef
from .rule_type import RuleType

if TYPE_CHECKING:
    from .pointers import Pointers

__all__ = ["RuleRef", "RuleType"]

Colorize = Callable[[Union[str, int], str], str]


class PrintOpts:
    def __init__(
        self,
        colorize: Colorize,
        pointers: "Pointers | None" = None,
        show_position: "bool | None" = None,
    ):
        self.pointers = pointers
        self.colorize = colorize
        self.show_position = show_position


# A range is a two element list of code points, inclusive on both ends.
Range = List[int]


class Rule:
    type: RuleType

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Rule, RuleRef)):
            return NotImplemented
        return type(self) is type(other) and getattr(self, "value", None) == getattr(
            other, "value", None
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


class RuleWithListOfIntsOrRanges(Rule):
    def __init__(self, value: List[Union[int, Range]]):
        # rules coming in are mutated as ranges and alternates are folded into them;
        # take a copy so that callers holding onto the original list are unaffected.
        self.value = list(validate_non_empty(value))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class RuleChar(RuleWithListOfIntsOrRanges):
    def __init__(self, value: List[Union[int, Range]]):
        self.type = RuleType.CHAR
        super().__init__(value)


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    def __init__(self, value: List[Union[int, Range]]):
        self.type = RuleType.CHAR_EXCLUDE
        super().__init__(value)


class RuleEnd(Rule):
    def __init__(self) -> None:
        self.type = RuleType.END

    def __repr__(self) -> str:
        return "RuleEnd()"


UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]
