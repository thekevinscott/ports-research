from __future__ import annotations

from .types import (
    InternalRuleDef,
    InternalRuleType,
)


def is_rule_def_type(type=None) -> bool:
    if not type:
        return False
    if isinstance(type, InternalRuleType):
        return True
    return type in {member.value for member in InternalRuleType}


def is_rule_def(rule=None) -> bool:
    return isinstance(rule, InternalRuleDef) and is_rule_def_type(rule.type)


def _is(rule, type: InternalRuleType) -> bool:
    return rule is not None and getattr(rule, "type", None) == type


def is_rule_def_alt(rule=None) -> bool:
    return _is(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule=None) -> bool:
    return _is(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule=None) -> bool:
    return _is(rule, InternalRuleType.END)


def is_rule_def_char(rule=None) -> bool:
    return _is(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule=None) -> bool:
    return _is(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule=None) -> bool:
    return _is(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule=None) -> bool:
    return _is(rule, InternalRuleType.CHAR_RNG_UPPER)
