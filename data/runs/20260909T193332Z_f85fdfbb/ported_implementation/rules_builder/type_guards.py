from __future__ import annotations

from typing import Any

from .types import InternalRuleDef, InternalRuleType


def is_rule_def_type(type_: Any = None) -> bool:
    if not type_:
        return False
    return type_ in tuple(InternalRuleType)


def is_rule_def(rule: Any = None) -> bool:
    if isinstance(rule, InternalRuleDef):
        return is_rule_def_type(rule.type)
    if isinstance(rule, dict) and "type" in rule:
        return is_rule_def_type(rule["type"])
    return False


def _is(rule: Any, type_: InternalRuleType) -> bool:
    return rule is not None and getattr(rule, "type", None) == type_


def is_rule_def_alt(rule: Any = None) -> bool:
    return _is(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule: Any = None) -> bool:
    return _is(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule: Any = None) -> bool:
    return _is(rule, InternalRuleType.END)


def is_rule_def_char(rule: Any = None) -> bool:
    return _is(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule: Any = None) -> bool:
    return _is(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule: Any = None) -> bool:
    return _is(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule: Any = None) -> bool:
    return _is(rule, InternalRuleType.CHAR_RNG_UPPER)
