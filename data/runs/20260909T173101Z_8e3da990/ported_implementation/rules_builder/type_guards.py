from __future__ import annotations

from typing import Any

from .types import InternalRuleDef, InternalRuleType


def is_rule_def_type(type_: Any = None) -> bool:
    if not type_:
        return False
    return type_ in tuple(InternalRuleType)


def is_rule_def(rule: Any = None) -> bool:
    return bool(rule) and isinstance(rule, InternalRuleDef) and is_rule_def_type(rule.type)


def is_rule_def_alt(rule: InternalRuleDef | None = None) -> bool:
    return rule is not None and rule.type == InternalRuleType.ALT


def is_rule_def_ref(rule: InternalRuleDef | None = None) -> bool:
    return rule is not None and rule.type == InternalRuleType.RULE_REF


def is_rule_def_end(rule: InternalRuleDef | None = None) -> bool:
    return rule is not None and rule.type == InternalRuleType.END


def is_rule_def_char(rule: InternalRuleDef | None = None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR


def is_rule_def_char_not(rule: InternalRuleDef | None = None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_NOT


def is_rule_def_char_alt(rule: InternalRuleDef | None = None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_ALT


def is_rule_def_char_rng_upper(rule: InternalRuleDef | None = None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_RNG_UPPER


# JS-name aliases for parity with the reference implementation.
isRuleDefType = is_rule_def_type
isRuleDef = is_rule_def
isRuleDefAlt = is_rule_def_alt
isRuleDefRef = is_rule_def_ref
isRuleDefEnd = is_rule_def_end
isRuleDefChar = is_rule_def_char
isRuleDefCharNot = is_rule_def_char_not
isRuleDefCharAlt = is_rule_def_char_alt
isRuleDefCharRngUpper = is_rule_def_char_rng_upper
