from __future__ import annotations

from typing import Any

from .types import InternalRuleDef, InternalRuleType


def is_rule_def_type(type_: Any = None) -> bool:
    if not type_:
        return False
    try:
        return type_ in [t.value for t in InternalRuleType]
    except TypeError:
        return False


def is_rule_def(rule: Any = None) -> bool:
    return bool(rule) and isinstance(rule, dict) and 'type' in rule and is_rule_def_type(rule['type'])


def _is_type(rule: Any, type_: InternalRuleType) -> bool:
    return rule is not None and rule['type'] == type_


def is_rule_def_alt(rule: InternalRuleDef = None) -> bool:
    return _is_type(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule: InternalRuleDef = None) -> bool:
    return _is_type(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule: InternalRuleDef = None) -> bool:
    return _is_type(rule, InternalRuleType.END)


def is_rule_def_char(rule: InternalRuleDef = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule: InternalRuleDef = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule: InternalRuleDef = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule: InternalRuleDef = None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_RNG_UPPER)
