from typing import Any, Optional

from .types import InternalRuleDef, InternalRuleType


def is_rule_def_type(type_: Any = None) -> bool:
    if not type_:
        return False
    return type_ in set(InternalRuleType)


def is_rule_def(rule: Any = None) -> bool:
    return bool(rule) and isinstance(rule, dict) and is_rule_def_type(rule.get("type"))


def _is_type(rule: Optional[InternalRuleDef], type_: InternalRuleType) -> bool:
    return rule is not None and rule["type"] == type_


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
