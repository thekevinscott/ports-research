from __future__ import annotations

from enum import StrEnum
from typing import Any, Dict, List, Union


class InternalRuleType(StrEnum):
    CHAR = 'CHAR'
    CHAR_RNG_UPPER = 'CHAR_RNG_UPPER'
    # CHAR_RNG = 'CHAR_RNG'
    RULE_REF = 'RULE_REF'
    ALT = 'ALT'
    END = 'END'

    CHAR_NOT = 'CHAR_NOT'
    CHAR_ALT = 'CHAR_ALT'


# Internal rule definitions are plain `{ 'type': ..., 'value': ... }` mappings,
# mirroring the object literals used by the reference implementation.
InternalRuleDef = Dict[str, Any]
