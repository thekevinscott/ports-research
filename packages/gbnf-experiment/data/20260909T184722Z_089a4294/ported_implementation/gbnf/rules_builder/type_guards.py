from __future__ import annotations

from .types import InternalRuleDef, InternalRuleType


def is_rule_def_type(type_: object) -> bool:
    return bool(type_) and type_ in tuple(InternalRuleType)


def is_rule_def(rule: object) -> bool:
    return isinstance(rule, dict) and "type" in rule and is_rule_def_type(rule["type"])


def _is_type(rule: InternalRuleDef | None, type_: InternalRuleType) -> bool:
    return rule is not None and rule["type"] == type_


def is_rule_def_alt(rule: InternalRuleDef | None) -> bool:
    return _is_type(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule: InternalRuleDef | None) -> bool:
    return _is_type(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule: InternalRuleDef | None) -> bool:
    return _is_type(rule, InternalRuleType.END)


def is_rule_def_char(rule: InternalRuleDef | None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule: InternalRuleDef | None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule: InternalRuleDef | None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule: InternalRuleDef | None) -> bool:
    return _is_type(rule, InternalRuleType.CHAR_RNG_UPPER)
