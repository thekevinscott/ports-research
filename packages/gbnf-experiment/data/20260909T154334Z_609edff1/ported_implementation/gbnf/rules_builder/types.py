from enum import Enum
from typing import Any, Dict, List

InternalRuleDef = Dict[str, Any]


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"


def rule_def(type_: InternalRuleType, value: Any = None) -> InternalRuleDef:
    if value is None:
        return {"type": type_}
    return {"type": type_, "value": value}


InternalRuleDefs = List[InternalRuleDef]
