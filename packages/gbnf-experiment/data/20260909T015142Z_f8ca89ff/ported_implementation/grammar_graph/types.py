from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Sequence, Union

from ..utils.js_compat import json_stringify
from .rule_ref import RuleRef

if TYPE_CHECKING:  # pragma: no cover
    from .generic_set import GenericSet
    from .graph_pointer import GraphPointer

__all__ = [
    "RuleType",
    "Range",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleRef",
    "UnresolvedRule",
    "ResolvedRule",
    "ValidInput",
    "Pointers",
]


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:  # so f-strings render the value, as in JS
        return self.value


# A `Range` is a two element sequence of code points, inclusive on both ends.
Range = Sequence[int]


class Rule:
    """Base class for the rules exposed to consumers.

    Instances compare equal to other rules with the same type/value, and also to
    plain mappings (``{'type': 'char', 'value': [...]}``), which keeps them easy
    to assert against.
    """

    type: RuleType
    __slots__ = ()

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

    def to_json(self) -> str:
        return json_stringify(self.to_dict())

    # Mapping-ish access, so `rule['type']` and `dict(rule)` both work.
    def keys(self):
        return self.to_dict().keys()

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Rule):
            return self.to_dict() == other.to_dict()
        if isinstance(other, Mapping):
            return self.to_dict() == dict(other)
        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self) -> int:
        return hash(self.to_json())


class _RuleWithValue(Rule):
    __slots__ = ("value",)

    def __init__(self, value: Sequence[Union[int, Range]] = ()):
        self.value: List[Union[int, Range]] = list(value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "value": [list(v) if isinstance(v, (list, tuple)) else v for v in self.value],
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value!r})"


class RuleChar(_RuleWithValue):
    type = RuleType.CHAR
    __slots__ = ()


class RuleCharExclude(_RuleWithValue):
    type = RuleType.CHAR_EXCLUDE
    __slots__ = ()


class RuleEnd(Rule):
    type = RuleType.END
    __slots__ = ()

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.value}

    def __repr__(self) -> str:
        return "RuleEnd()"


# RuleRefs are never exposed to the end user.
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, Sequence[int]]

if TYPE_CHECKING:  # pragma: no cover
    Pointers = "GenericSet[GraphPointer, str]"
else:
    Pointers = Any
