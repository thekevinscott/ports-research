import json
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Union

from .rule_ref import RuleRef

Colorize = Callable[[Union[str, int], str], str]


@dataclass
class PrintOpts:
    colorize: "Colorize"
    pointers: Optional[Any] = None
    show_position: bool = False

# A range is a two element list of code points, inclusive on both ends.
Range = List[int]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


def values_are_equal(left: Any, right: Any) -> bool:
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            values_are_equal(value, right[idx]) for idx, value in enumerate(left)
        )
    return left == right


class Rule:
    _type_name = "Rule"

    def __init__(self) -> None:
        # `type` lives on the instance so that `rule.__dict__` is the serialized
        # form of the rule, which is what de-duplication keys off of.
        self.type = self._type_name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self))

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"{self.type}()"


class RuleWithValue(Rule):
    _type_name = "RuleWithValue"

    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and values_are_equal(self.value, other.value)

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"{self.type}(value={json.dumps(self.value)})"


class RuleWithListOfIntsOrRanges(RuleWithValue):
    _type_name = "RuleWithListOfIntsOrRanges"

    def __init__(self, value: List[Union[int, Range]] = None) -> None:
        super().__init__(list(value) if value is not None else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    _type_name = "RuleChar"


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    _type_name = "RuleCharExclude"


class RuleEnd(Rule):
    _type_name = "RuleEnd"


# RuleRefs should never be exposed to the end user.
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]
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
    "values_are_equal",
]
