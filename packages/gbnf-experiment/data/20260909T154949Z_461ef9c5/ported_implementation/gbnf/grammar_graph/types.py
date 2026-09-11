"""Rule types exposed by the graph.

Mirrors ``src/grammar-graph/types.ts``. ``Range`` is modelled as a two element
list so that it round-trips through ``as_dict`` the way the JS arrays did.
"""
from __future__ import annotations

import json
from enum import Enum
from typing import TYPE_CHECKING, Iterable, List, Union

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .rule_ref import RuleRef


class RuleType(str, Enum):
    CHAR = 'char'
    CHAR_EXCLUDE = 'char_exclude'
    END = 'end'


Range = List[int]
CodePointOrRange = Union[int, Range]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


def _serialize_value(value: Iterable[CodePointOrRange]) -> str:
    return json.dumps(value, separators=(',', ':'))


class _Rule:
    """Base for the value-typed rules.

    The graph de-duplicates structurally identical rules onto a single instance,
    so value based equality/hashing is equivalent to the identity semantics the
    JS ``Map<UnresolvedRule, ...>`` lookups relied on.
    """

    type: RuleType

    def _key(self):
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Rule):
            return self._key() == other._key()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._key())


class _CharRule(_Rule):
    def __init__(self, value: Iterable[CodePointOrRange] | None = None):
        self.value: List[CodePointOrRange] = list(value) if value is not None else []

    def _key(self):
        return (self.type.value, _serialize_value(self.value))

    def as_dict(self) -> dict:
        return {'type': self.type.value, 'value': [
            list(v) if isinstance(v, list) else v for v in self.value
        ]}

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'


class RuleChar(_CharRule):
    type = RuleType.CHAR


class RuleCharExclude(_CharRule):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd(_Rule):
    type = RuleType.END

    def _key(self):
        return (self.type.value,)

    def as_dict(self) -> dict:
        return {'type': self.type.value}

    def __repr__(self) -> str:
        return 'RuleEnd()'


# RuleRefs should never be exposed to the end user.
UnresolvedRule = Union[RuleChar, RuleCharExclude, 'RuleRef', RuleEnd]
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]
