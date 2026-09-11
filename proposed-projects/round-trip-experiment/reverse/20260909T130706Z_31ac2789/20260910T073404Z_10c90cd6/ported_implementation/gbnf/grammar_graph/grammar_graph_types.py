from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from .rule_ref import RuleRef
from .rule_type import RuleType

# A range of code points, inclusive on both ends: [start, end].
Range = List[int]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like
# "8") should be passed in as a string.
ValidInput = Union[str, int, List[int]]

T = TypeVar("T")


class Rule:
    type: str

    def equals(self, other: object) -> bool:
        return isinstance(other, type(self)) and type(other) is type(self)

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": self.type,
        }

    toJSON = to_json

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return NotImplemented
        return type(other) is type(self)

    def __hash__(self) -> int:
        return hash(type(self))

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class RuleWithValue(Rule, Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def equals(self, other: object) -> bool:
        return type(other) is type(self) and other.value == self.value

    def to_json(self) -> Dict[str, Any]:
        return {
            **Rule.to_json(self),
            "value": self.value,
        }

    toJSON = to_json

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return NotImplemented
        return type(other) is type(self) and other.value == self.value

    def __hash__(self) -> int:
        return hash((type(self), repr(self.value)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class RuleWithListOfIntsOrRanges(RuleWithValue[List[Union[int, Range]]]):
    def __init__(self, value: Optional[List[Union[int, Range]]] = None):
        super().__init__(list(value) if value is not None else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    type = RuleType.CHAR


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd(Rule):
    type = RuleType.END


# RuleRefs should never be exposed to the end user.
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]
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
    "RuleWithValue",
    "UnresolvedRule",
    "ValidInput",
]
