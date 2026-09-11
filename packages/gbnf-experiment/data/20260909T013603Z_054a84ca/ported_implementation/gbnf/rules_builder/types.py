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


class InternalRuleDef:
    """A single element of a linear (pre-stacked) rule definition.

    ``value`` is a list of code points for CHAR/CHAR_NOT, a single code point
    for CHAR_ALT/CHAR_RNG_UPPER, a rule id for RULE_REF, and absent for
    ALT/END.
    """

    __slots__ = ('type', 'value')

    def __init__(
        self,
        type: InternalRuleType,
        value: Optional[Union[int, List[int]]] = None,
    ):
        self.type = type
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InternalRuleDef):
            return NotImplemented
        return self.type == other.type and self.value == other.value

    def __repr__(self) -> str:
        if self.value is None:
            return f'InternalRuleDef({self.type.value})'
        return f'InternalRuleDef({self.type.value}, {self.value!r})'
