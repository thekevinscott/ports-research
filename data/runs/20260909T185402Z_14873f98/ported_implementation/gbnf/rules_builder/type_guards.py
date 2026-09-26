from .types import ALL_INTERNAL_RULE_TYPES, InternalRuleDef, InternalRuleType


def is_rule_def_type(type_=None) -> bool:
    return bool(type_) and type_ in ALL_INTERNAL_RULE_TYPES


def is_rule_def(rule=None) -> bool:
    return isinstance(rule, InternalRuleDef) and is_rule_def_type(rule.type)


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
