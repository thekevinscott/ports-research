class InternalRuleType:
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"


ALL_INTERNAL_RULE_TYPES = frozenset(
    {
        InternalRuleType.CHAR,
        InternalRuleType.CHAR_RNG_UPPER,
        InternalRuleType.RULE_REF,
        InternalRuleType.ALT,
        InternalRuleType.END,
        InternalRuleType.CHAR_NOT,
        InternalRuleType.CHAR_ALT,
    }
)


class InternalRuleDef:
    """A rule definition emitted by the rules builder.

    `value` is a list of code points for CHAR/CHAR_NOT, a single number for
    RULE_REF/CHAR_ALT/CHAR_RNG_UPPER, and absent for ALT/END.
    """

    __slots__ = ("type", "value")

    def __init__(self, type_: str, value=None):
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type})"
        return f"InternalRuleDef({self.type}, {self.value})"
