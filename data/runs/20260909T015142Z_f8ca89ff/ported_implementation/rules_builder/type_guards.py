from __future__ import annotations

from typing import Any

from .types import InternalRuleDef, InternalRuleType

__all__ = [
    "is_rule_def_type",
    "is_rule_def",
    "is_rule_def_alt",
    "is_rule_def_ref",
    "is_rule_def_end",
    "is_rule_def_char",
    "is_rule_def_char_not",
    "is_rule_def_char_alt",
    "is_rule_def_char_rng_upper",
]

_INTERNAL_RULE_TYPE_VALUES = {member.value for member in InternalRuleType}


def _type_of(rule: Any) -> Any:
    if isinstance(rule, dict):
        return rule.get("type")
    return getattr(rule, "type", None)


def is_rule_def_type(type_: Any = None) -> bool:
    if not type_:
        return False
    if isinstance(type_, InternalRuleType):
        return True
    return type_ in _INTERNAL_RULE_TYPE_VALUES


def is_rule_def(rule: Any = None) -> bool:
    if rule is None:
        return False
    if isinstance(rule, InternalRuleDef):
        return True
    if isinstance(rule, dict):
        return "type" in rule and is_rule_def_type(rule["type"])
    return hasattr(rule, "type") and is_rule_def_type(rule.type)


def _is(rule: Any, type_: InternalRuleType) -> bool:
    return rule is not None and _type_of(rule) == type_


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


isRuleDefType = is_rule_def_type
isRuleDef = is_rule_def
isRuleDefAlt = is_rule_def_alt
isRuleDefRef = is_rule_def_ref
isRuleDefEnd = is_rule_def_end
isRuleDefChar = is_rule_def_char
isRuleDefCharNot = is_rule_def_char_not
isRuleDefCharAlt = is_rule_def_char_alt
isRuleDefCharRngUpper = is_rule_def_char_rng_upper
