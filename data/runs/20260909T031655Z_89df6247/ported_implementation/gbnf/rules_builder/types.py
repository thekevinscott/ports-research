from enum import Enum


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"


class InternalRuleDef:
    """A single linear rule definition, mirroring the reference's plain objects."""

    __slots__ = ("type", "value")

    def __init__(self, type: InternalRuleType, value=None):
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type.value})"
        return f"InternalRuleDef({self.type.value}, {self.value!r})"
