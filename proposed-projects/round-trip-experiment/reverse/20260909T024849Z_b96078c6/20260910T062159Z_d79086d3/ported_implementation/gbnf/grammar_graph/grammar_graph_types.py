from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Union

# A `Range` is an inclusive `[start, end]` pair of code points.
Range = List[int]

# The value carried by a char rule: code points and/or inclusive ranges.
RuleCharValue = List[Union[int, Range]]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input
# (like "8") should be passed in as a string.
ValidInput = Union[str, int, List[int]]


class PrintOpts:
    """Options for `GraphNode.print` / `GraphPointer.print`."""

    def __init__(
        self,
        colorize: Callable[[Any, str], str],
        pointers: Optional[Any] = None,
        show_position: bool = False,
    ) -> None:
        self.colorize = colorize
        self.pointers = pointers
        self.show_position = show_position


class Rule:
    def __init__(self) -> None:
        # `type` is a real attribute, so that `rule.__dict__` round-trips to JSON as
        # `{"type": ..., "value": ...}`.
        self.type = type(self).__name__

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.__dict__ == other.__dict__

    # Rules are used as identity keys while walking the graph, so hashing stays
    # identity based even though equality is structural.
    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{self.type}()"


class RuleWithValue(Rule):
    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return f"{self.type}(value={json.dumps(self.value)})"


class RuleWithListOfIntsOrRanges(RuleWithValue):
    def __init__(self, value: Optional[RuleCharValue] = None) -> None:
        super().__init__(list(value) if value else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    pass


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    pass


class RuleEnd(Rule):
    pass


# UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
# ResolvedRule = RuleChar | RuleCharExclude | RuleEnd; RuleRefs should never be
# exposed to the end user.
UnresolvedRule = Any
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]
ResolvedGraphPointer = Any

RuleDict = Dict[str, Any]
