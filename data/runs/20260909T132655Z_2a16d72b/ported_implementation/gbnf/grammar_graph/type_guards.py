from .rule_ref import RuleRef
from .types import RuleType

RULE_TYPES = {RuleType.CHAR, RuleType.CHAR_EXCLUDE, RuleType.END}


def is_rule_type(type_: object) -> bool:
    return bool(type_) and type_ in RULE_TYPES


def is_rule(rule: object) -> bool:
    return (
        rule is not None
        and (isinstance(rule, RuleRef) or is_rule_type(getattr(rule, "type", None)))
    )


def is_rule_ref(rule: object) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: object) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and getattr(rule, "type", None) == RuleType.END
    )


def is_rule_char(rule: object) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and getattr(rule, "type", None) == RuleType.CHAR
    )


def is_rule_char_excluded(rule: object) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and getattr(rule, "type", None) == RuleType.CHAR_EXCLUDE
    )


def is_range(rng: object) -> bool:
    return (
        isinstance(rng, (list, tuple))
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
