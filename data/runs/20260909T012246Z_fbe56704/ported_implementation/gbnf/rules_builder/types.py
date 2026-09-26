from enum import Enum
from typing import List, Optional, Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:
        return self.value


class InternalRuleDef:
    """A single element of a linear (pre-stacked) rule definition.

    CHAR and CHAR_NOT carry a list of code points; RULE_REF, CHAR_ALT and
    CHAR_RNG_UPPER carry a single number; ALT and END carry no value.
    """

    __slots__ = ("type", "value")

    def __init__(
        self,
        type: InternalRuleType,
        value: Optional[Union[int, List[int]]] = None,
    ):
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type})"
        return f"InternalRuleDef({self.type}, {self.value!r})"
