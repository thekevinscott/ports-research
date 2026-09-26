from __future__ import annotations

import json
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Iterator, List, Sequence, Union

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .generic_set import GenericSet
    from .graph_pointer import GraphPointer
    from .rule_ref import RuleRef


class RuleType(StrEnum):
    CHAR = 'char'
    CHAR_EXCLUDE = 'char_exclude'
    END = 'end'


# A range is a two element `[start, end]` list of code points.
Range = List[int]


class _Rule:
    """Base class for the rules handed back to the caller.

    The reference exposes plain `{ type, value }` objects. These behave like
    those objects: they compare equal to the equivalent dict, support
    `rule['type']` lookups and can be passed to `dict()`.
    """

    type: RuleType
    __slots__ = ()

    def to_dict(self) -> dict:
        raise NotImplementedError

    def keys(self):
        return self.to_dict().keys()

    def __getitem__(self, key: str) -> Any:
        try:
            return self.to_dict()[key]
        except KeyError:
            raise KeyError(key) from None

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Rule):
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == other
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self) -> int:
        return hash(json.dumps(self.to_dict(), separators=(',', ':')))

    def __repr__(self) -> str:
        parts = [
            f"type='{value}'" if key == 'type' else f'{key}={value!r}'
            for key, value in self.to_dict().items()
        ]
        return f'{type(self).__name__}({", ".join(parts)})'


class RuleChar(_Rule):
    type = RuleType.CHAR
    __slots__ = ('value',)

    def __init__(self, value: Sequence[Union[int, Range]] = ()):
        self.value: List[Union[int, Range]] = list(value)

    def to_dict(self) -> dict:
        return {'type': self.type, 'value': self.value}


class RuleCharExclude(_Rule):
    type = RuleType.CHAR_EXCLUDE
    __slots__ = ('value',)

    def __init__(self, value: Sequence[Union[int, Range]] = ()):
        self.value: List[Union[int, Range]] = list(value)

    def to_dict(self) -> dict:
        return {'type': self.type, 'value': self.value}


class RuleEnd(_Rule):
    type = RuleType.END
    __slots__ = ()

    def to_dict(self) -> dict:
        return {'type': self.type}


# RuleRefs should never be exposed to the end user.
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd, 'RuleRef']
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]

if TYPE_CHECKING:  # pragma: no cover - typing only
    ResolvedGraphPointer = 'GraphPointer'
    Pointers = 'GenericSet[GraphPointer, str]'

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]
