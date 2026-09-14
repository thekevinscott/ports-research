from enum import Enum


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
    """A plain record of a rule type and, for most types, a value."""

    __slots__ = ("type", "value")

    _MISSING = object()

    def __init__(self, type_: InternalRuleType, value=_MISSING):
        self.type = type_
        self.value = None if value is InternalRuleDef._MISSING else value

    def __repr__(self) -> str:
        if self.value is None:
            return f"{{type: {self.type}}}"
        return f"{{type: {self.type}, value: {self.value!r}}}"
