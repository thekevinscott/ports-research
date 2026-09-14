from __future__ import annotations

from enum import StrEnum
from typing import Any


class InternalRuleType(StrEnum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"


# Internal rule definitions are plain dicts of the shape
# `{"type": InternalRuleType, "value": int | list[int]}`, where ALT and END carry no value.
InternalRuleDef = dict[str, Any]
