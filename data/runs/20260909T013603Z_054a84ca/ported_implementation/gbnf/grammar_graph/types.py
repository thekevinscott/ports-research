from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict, Iterable, List, Sequence, Union


class RuleType(str, Enum):
    CHAR = 'char'
    CHAR_EXCLUDE = 'char_exclude'
    END = 'end'


# A range is a two element [start, end] pair of code points.
Range = List[int]
RuleValue = Union[int, Range]
# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number"
# (like "8") should be passed in as a string.
ValidInput = Union[str, int, Sequence[int]]


class Rule:
    """Base class for the rules exposed to consumers of a `ParseState`.

    Rules use identity comparison (as object references do in the reference
    implementation); the graph relies on that to dedupe and to group pointers.
    """

    type: RuleType

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

    def serialize(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'))


class _RuleWithValue(Rule):
    __slots__ = ('value',)

    def __init__(self, value: Iterable[RuleValue] = ()):
        self.value: List[RuleValue] = [
            list(v) if isinstance(v, (list, tuple)) else v for v in value
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.value,
            'value': [list(v) if isinstance(v, list) else v for v in self.value],
        }

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'


class RuleChar(_RuleWithValue):
    type = RuleType.CHAR


class RuleCharExclude(_RuleWithValue):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd(Rule):
    __slots__ = ()
    type = RuleType.END

    def to_dict(self) -> Dict[str, Any]:
        return {'type': self.type.value}

    def __repr__(self) -> str:
        return 'RuleEnd()'
