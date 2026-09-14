from .types import InternalRuleType

_INTERNAL_RULE_TYPE_VALUES = {member.value for member in InternalRuleType}


def is_rule_def_type(type_=None) -> bool:
    return bool(type_) and type_ in _INTERNAL_RULE_TYPE_VALUES


def is_rule_def(rule=None) -> bool:
    return rule is not None and hasattr(rule, "type") and is_rule_def_type(rule.type)


def is_rule_def_alt(rule=None) -> bool:
    return rule is not None and rule.type == InternalRuleType.ALT


def is_rule_def_ref(rule=None) -> bool:
    return rule is not None and rule.type == InternalRuleType.RULE_REF


def is_rule_def_end(rule=None) -> bool:
    return rule is not None and rule.type == InternalRuleType.END


def is_rule_def_char(rule=None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR


def is_rule_def_char_not(rule=None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_NOT


def is_rule_def_char_alt(rule=None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_ALT


def is_rule_def_char_rng_upper(rule=None) -> bool:
    return rule is not None and rule.type == InternalRuleType.CHAR_RNG_UPPER
