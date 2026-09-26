from .types import InternalRuleType

INTERNAL_RULE_TYPES = {
    InternalRuleType.CHAR,
    InternalRuleType.CHAR_RNG_UPPER,
    InternalRuleType.RULE_REF,
    InternalRuleType.ALT,
    InternalRuleType.END,
    InternalRuleType.CHAR_NOT,
    InternalRuleType.CHAR_ALT,
}


def is_rule_def_type(type_: object) -> bool:
    return bool(type_) and type_ in INTERNAL_RULE_TYPES


def is_rule_def(rule: object) -> bool:
    return rule is not None and is_rule_def_type(getattr(rule, "type", None))


def _is(rule, type_: str) -> bool:
    return rule is not None and rule.type == type_


def is_rule_def_alt(rule) -> bool:
    return _is(rule, InternalRuleType.ALT)


def is_rule_def_ref(rule) -> bool:
    return _is(rule, InternalRuleType.RULE_REF)


def is_rule_def_end(rule) -> bool:
    return _is(rule, InternalRuleType.END)


def is_rule_def_char(rule) -> bool:
    return _is(rule, InternalRuleType.CHAR)


def is_rule_def_char_not(rule) -> bool:
    return _is(rule, InternalRuleType.CHAR_NOT)


def is_rule_def_char_alt(rule) -> bool:
    return _is(rule, InternalRuleType.CHAR_ALT)


def is_rule_def_char_rng_upper(rule) -> bool:
    return _is(rule, InternalRuleType.CHAR_RNG_UPPER)
