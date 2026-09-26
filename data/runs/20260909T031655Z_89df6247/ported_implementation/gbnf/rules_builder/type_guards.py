from .types import InternalRuleDef, InternalRuleType


def is_rule_def_type(type_=None) -> bool:
    return bool(type_) and type_ in tuple(InternalRuleType)


def is_rule_def(rule=None) -> bool:
    return isinstance(rule, InternalRuleDef) and is_rule_def_type(rule.type)


def _is(rule, type_) -> bool:
    return rule is not None and rule.type == type_


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
