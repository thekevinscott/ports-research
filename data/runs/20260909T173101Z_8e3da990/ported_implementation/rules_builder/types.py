from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InternalRuleType(StrEnum):
    CHAR = 'CHAR'
    CHAR_RNG_UPPER = 'CHAR_RNG_UPPER'
    RULE_REF = 'RULE_REF'
    ALT = 'ALT'
    END = 'END'

    CHAR_NOT = 'CHAR_NOT'
    CHAR_ALT = 'CHAR_ALT'


@dataclass
class InternalRuleDef:
    """A single entry of a linearized rule.

    The reference implementation models these as a union of plain objects; the
    shape only ever varies in whether `value` is a list of code points
    (CHAR/CHAR_NOT), a single code point or rule id (CHAR_ALT/CHAR_RNG_UPPER/
    RULE_REF), or absent (ALT/END).
    """

    type: InternalRuleType
    value: int | float | list[int | float] | None = None
