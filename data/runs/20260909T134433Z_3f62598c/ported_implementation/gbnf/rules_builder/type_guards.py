from typing import Any

from .types import (
    InternalRuleDefAlt,
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefEnd,
    InternalRuleDefReference,
    InternalRuleType,
)


def is_rule_def_type(type_: Any = None) -> bool:
    if isinstance(type_, InternalRuleType):
        return True
    return isinstance(type_, str) and type_ in {t.value for t in InternalRuleType}


def is_rule_def(rule: Any = None) -> bool:
    return rule is not None and hasattr(rule, "type") and is_rule_def_type(rule.type)


def is_rule_def_alt(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
