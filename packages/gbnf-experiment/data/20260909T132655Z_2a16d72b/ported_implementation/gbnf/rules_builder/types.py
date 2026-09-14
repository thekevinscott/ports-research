from typing import List, Optional, Union


class InternalRuleType:
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"


class InternalRuleDef:
    """A single entry in the linear rule definition list.

    ``value`` is a list of code points for CHAR/CHAR_NOT, a single number for
    CHAR_ALT/CHAR_RNG_UPPER/RULE_REF, and absent for ALT/END.
    """

    __slots__ = ("type", "value")

    def __init__(self, type: str, value: Optional[Union[int, List[int]]] = None):
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type})"
        return f"InternalRuleDef({self.type}, {self.value!r})"
