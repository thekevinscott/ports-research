from typing import List, Union

from .rule_ref import RuleRef

# A range is a two element list of code points, inclusive on both ends.
Range = List[int]


class Rule:
    """Base class for every rule exposed by the graph.

    `type` is deliberately only reachable through the `__dict__` property. The
    instance dictionary itself holds `value` (and nothing else), so `rule.type`
    raises an `AttributeError` even though `rule.__dict__["type"]` is present.
    """

    # Rules are keyed by identity when grouping pointers, so keep the default
    # identity hash even though `__eq__` is defined.
    __hash__ = object.__hash__

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self))

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    @property
    def __dict__(self):
        return {"type": type(self).__name__}


class RuleWithValue(Rule):
    __hash__ = object.__hash__

    def __init__(self, value):
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"

    @property
    def __dict__(self):
        return {"type": type(self).__name__, "value": self.value}


class RuleWithListOfIntsOrRanges(RuleWithValue):
    def __init__(self, value: Union[List[Union[int, Range]], None] = None):
        # Copy the incoming list: `build_rule_stack` mutates `value` while
        # collecting ranges and alternates, and must not touch the caller's list.
        super().__init__(list(value) if value is not None else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    pass


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    pass


class RuleEnd(Rule):
    pass


# RuleRefs should never be exposed to the end user.
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like
# "8") should be passed in as a string.
ValidInput = Union[str, int, List[int]]

__all__ = [
    "Range",
    "ResolvedRule",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleRef",
    "RuleWithValue",
    "RuleWithListOfIntsOrRanges",
    "UnresolvedRule",
    "ValidInput",
]
