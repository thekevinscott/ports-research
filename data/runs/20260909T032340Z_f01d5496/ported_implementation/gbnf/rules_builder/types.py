from enum import Enum
from typing import Any, Dict, List, Optional, Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


class InternalRuleDef:
    """A rule definition emitted by the RulesBuilder.

    ``value`` is a list of code points for CHAR/CHAR_NOT, a single code point for
    CHAR_ALT/CHAR_RNG_UPPER, a rule id for RULE_REF, and absent for ALT/END.
    """

    __slots__ = ("type", "value")

    def __init__(
        self,
        type_: InternalRuleType,
        value: Optional[Union[int, List[int]]] = None,
    ):
        self.type = type_
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, InternalRuleDef):
            return NotImplemented
        return self.type == other.type and self.value == other.value

    def __hash__(self) -> int:
        value = tuple(self.value) if isinstance(self.value, list) else self.value
        return hash((self.type, value))

    def to_dict(self) -> Dict[str, Any]:
        if self.value is None:
            return {"type": self.type}
        return {"type": self.type, "value": self.value}

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type.value})"
        return f"InternalRuleDef({self.type.value}, {self.value!r})"
