from enum import Enum
from typing import Any, Optional


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_ALT = "CHAR_ALT"
    CHAR_NOT = "CHAR_NOT"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    ALT = "ALT"
    END = "END"
    RULE_REF = "RULE_REF"


# Internal rule definitions are plain dicts of the shape:
#   {"type": InternalRuleType.CHAR, "value": [int]}
#   {"type": InternalRuleType.CHAR_NOT, "value": [int]}
#   {"type": InternalRuleType.CHAR_ALT, "value": int}
#   {"type": InternalRuleType.CHAR_RNG_UPPER, "value": int}
#   {"type": InternalRuleType.RULE_REF, "value": int}
#   {"type": InternalRuleType.ALT}
#   {"type": InternalRuleType.END}
InternalRuleDef = dict[str, Any]


def _is_type(rule: Optional[InternalRuleDef], type_: InternalRuleType) -> bool:
    return rule is not None and rule.get("type") == type_


def is_rule_def_alt(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is_type(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is_type(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is_type(rule, InternalRuleType.END)


def is_rule_def_char(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_RNG_UPPER)
