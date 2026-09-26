from typing import Any, Optional

from .types import InternalRuleDef, InternalRuleType


def is_rule_def_type(type: Any = None) -> bool:
    return bool(type) and type in tuple(InternalRuleType)


def is_rule_def(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDef) and is_rule_def_type(rule.type)


def _is(rule: Optional[InternalRuleDef], type: InternalRuleType) -> bool:
    return rule is not None and rule.type == type


def is_rule_def_alt(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is(rule, InternalRuleType.END)


def is_rule_def_char(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule: Optional[InternalRuleDef] = None) -> bool:
    return _is(rule, InternalRuleType.CHAR_RNG_UPPER)
