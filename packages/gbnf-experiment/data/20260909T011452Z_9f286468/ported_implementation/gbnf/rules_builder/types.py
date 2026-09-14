from enum import Enum
from typing import List, Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    # CHAR_RNG = 'CHAR_RNG'
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


class InternalRuleDef:
    __slots__ = ("type", "value")

    def __init__(self, type: InternalRuleType, value: Union[int, List[int], None] = None):
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type.value})"
        return f"InternalRuleDef({self.type.value}, {self.value!r})"
