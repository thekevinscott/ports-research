from .rule_ref import RuleRef
from .types import ALL_RULE_TYPES, RuleType


def is_rule_type(type_=None) -> bool:
    return bool(type_) and type_ in ALL_RULE_TYPES


def is_rule(rule=None) -> bool:
    return rule is not None and hasattr(rule, "type") and is_rule_type(rule.type)


def is_rule_ref(rule=None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule=None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.END


def is_rule_char(rule=None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.CHAR


def is_rule_char_excluded(rule=None) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and rule.type == RuleType.CHAR_EXCLUDE
    )


def is_range(rng=None) -> bool:
    return (
        isinstance(rng, list)
        and len(rng) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in rng)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_excluded(pointer.rule)
