"""Rule types exposed by the grammar graph.

Port of ``src/grammar-graph/types.ts``. The TypeScript original describes rules
as plain object literals; here they are small classes so that ``isinstance``
can stand in for the structural type guards.
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

    def __str__(self) -> str:
        return self.value


# A range is a two element list of code points, inclusive on both ends.
Range = List[int]
CodePointOrRange = Union[int, Range]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


class _ValuedRule:
    """Shared behaviour for the two rules that carry a list of code points."""

    type: RuleType
    __slots__ = ('value',)

    def __init__(self, value: Iterable[CodePointOrRange]) -> None:
        self.value: List[CodePointOrRange] = [
            list(v) if isinstance(v, (list, tuple)) else v for v in value
        ]

    def to_dict(self) -> dict:
        return {
            'type': self.type.value,
            'value': [list(v) if isinstance(v, list) else v for v in self.value],
        }

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _ValuedRule):
            return self.type is other.type and self.value == other.value
        if isinstance(other, dict):
            return self.to_dict() == other
        return NotImplemented

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'


class RuleChar(_ValuedRule):
    type = RuleType.CHAR


class RuleCharExclude(_ValuedRule):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd:
    type = RuleType.END
    __slots__ = ()

    def to_dict(self) -> dict:
        return {'type': self.type.value}

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RuleEnd):
            return True
        if isinstance(other, dict):
            return other == {'type': RuleType.END.value}
        return NotImplemented

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return 'RuleEnd()'


# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]
UnresolvedRule = Union[ResolvedRule, 'RuleRef']


def serialize_rule(rule: ResolvedRule) -> str:
    """Stable key for a resolved rule, mirroring ``JSON.stringify(rule)``."""
    return json.dumps(rule.to_dict(), separators=(',', ':'))
