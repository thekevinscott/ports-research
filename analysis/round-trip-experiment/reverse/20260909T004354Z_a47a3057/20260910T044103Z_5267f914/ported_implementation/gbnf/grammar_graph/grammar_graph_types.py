from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Sequence, Union

from ..utils.validate_non_empty import validate_non_empty
from .rule_ref import RuleRef

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode
    from .graph_pointer import GraphPointer
    from .pointers import Pointers


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    RULE_REF = "rule_ref"
    END = "end"


# A range is a two element list of code points, inclusive on both ends.
Range = List[int]


@dataclass
class PrintOpts:
    colorize: Callable[[Union[str, int], str], str]
    pointers: Optional["Pointers"] = None
    show_position: bool = False


class RuleWithListOfIntsOrRanges:
    type: str

    def __init__(self, value: Sequence[Union[int, Range]]):
        # the incoming list is copied so later mutations of the rule that produced
        # it cannot leak into this one.
        self.value: List[Union[int, Range]] = list(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleWithListOfIntsOrRanges):
            return NotImplemented
        return type(self) is type(other) and self.value == other.value

    def __hash__(self) -> int:
        return hash(
            (
                type(self).__name__,
                tuple(tuple(v) if isinstance(v, list) else v for v in self.value),
            )
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class RuleChar(RuleWithListOfIntsOrRanges):
    def __init__(self, value: Sequence[Union[int, Range]]):
        # `type` is set as an instance attribute so it shows up in `__dict__`.
        self.type = RuleType.CHAR
        super().__init__(value)


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    def __init__(self, value: Sequence[Union[int, Range]]):
        self.type = RuleType.CHAR_EXCLUDE
        super().__init__(value)


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleEnd):
            return NotImplemented
        return type(self) is type(other)

    def __hash__(self) -> int:
        return hash(RuleType.END)

    def __repr__(self) -> str:
        return "RuleEnd()"


UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]

RootNode = Dict[int, "GraphNode"]
ResolvedGraphPointer = "GraphPointer"

__all__ = [
    "PrintOpts",
    "Range",
    "ResolvedGraphPointer",
    "ResolvedRule",
    "RootNode",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleRef",
    "RuleType",
    "UnresolvedRule",
    "ValidInput",
    "validate_non_empty",
]
