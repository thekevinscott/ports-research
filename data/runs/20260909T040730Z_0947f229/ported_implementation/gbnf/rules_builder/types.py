"""Port of ``src/rules-builder/types.ts``.

The TypeScript original models internal rule definitions as a discriminated
union of object literals. Here a single mutable class carries the discriminant
plus an optional value, which keeps ``parse_sequence``'s list surgery close to
the original.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union


class InternalRuleType(str, Enum):
    CHAR = 'CHAR'
    CHAR_RNG_UPPER = 'CHAR_RNG_UPPER'
    RULE_REF = 'RULE_REF'
    ALT = 'ALT'
    END = 'END'

    CHAR_NOT = 'CHAR_NOT'
    CHAR_ALT = 'CHAR_ALT'

    def __str__(self) -> str:
        return self.value


InternalRuleValue = Union[int, List[int], None]


class InternalRuleDef:
    __slots__ = ('type', 'value')

    def __init__(self, type: InternalRuleType, value: InternalRuleValue = None) -> None:
        self.type = type
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InternalRuleDef):
            return NotImplemented
        return self.type is other.type and self.value == other.value

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        if self.value is None:
            return f'InternalRuleDef({self.type.value})'
        return f'InternalRuleDef({self.type.value}, {self.value!r})'


InternalRuleDefs = List[Optional[List[InternalRuleDef]]]
