"""Port of ``src/rules-builder/types.ts``."""
from __future__ import annotations

from enum import Enum
from typing import Any, List, Union


class InternalRuleType(str, Enum):
    CHAR = 'CHAR'
    CHAR_RNG_UPPER = 'CHAR_RNG_UPPER'
    RULE_REF = 'RULE_REF'
    ALT = 'ALT'
    END = 'END'

    CHAR_NOT = 'CHAR_NOT'
    CHAR_ALT = 'CHAR_ALT'


class InternalRuleDef:
    """``{ type, value? }`` — CHAR/CHAR_NOT carry a list, the rest a bare int."""

    __slots__ = ('type', 'value')

    _MISSING = object()

    def __init__(self, type: InternalRuleType, value: Any = _MISSING):
        self.type = type
        self.value: Union[int, List[int], None] = None if value is self._MISSING else value

    def __repr__(self) -> str:
        if self.value is None:
            return f'InternalRuleDef({self.type.value})'
        return f'InternalRuleDef({self.type.value}, {self.value!r})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InternalRuleDef):
            return NotImplemented
        return self.type == other.type and self.value == other.value
