from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Union

from .rule_ref import RuleRef

if TYPE_CHECKING:  # pragma: no cover
    from .pointers import Pointers

Colorize = Callable[[Union[str, int], str], str]

# A range is a two element list of code points, e.g. [ord('a'), ord('z')].
Range = list


@dataclass
class PrintOpts:
    colorize: Colorize
    pointers: Optional["Pointers"] = None
    show_position: bool = False


class Rule:
    @property
    def type(self) -> str:
        return "Rule"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type}

    def __repr__(self) -> str:
        return f"{self.type}()"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    __hash__ = None  # type: ignore[assignment]


class RuleWithValue(Rule):
    def __init__(self, value: Any):
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        return {**super().to_dict(), "value": self.value}

    def __repr__(self) -> str:
        return f"{self.type}(value={self.value!r})"


class RuleWithListOfIntsOrRanges(RuleWithValue):
    def __init__(self, value: Optional[Sequence[Union[int, list]]] = None):
        super().__init__(list(value) if value is not None else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    @property
    def type(self) -> str:
        return "RuleChar"


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    @property
    def type(self) -> str:
        return "RuleCharExclude"


class RuleEnd(Rule):
    @property
    def type(self) -> str:
        return "RuleEnd"


UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input
# (like "8") should be passed in as a string.
ValidInput = Union[str, int, list[int]]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

__all__ = [
    "Colorize",
    "PrintOpts",
    "Range",
    "ResolvedRule",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleRef",
    "RuleWithListOfIntsOrRanges",
    "RuleWithValue",
    "UnresolvedRule",
    "ValidInput",
]
