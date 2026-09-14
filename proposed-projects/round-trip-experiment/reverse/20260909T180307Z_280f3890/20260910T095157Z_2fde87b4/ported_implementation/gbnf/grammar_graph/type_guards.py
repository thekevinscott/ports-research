from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd, RuleType
from .rule_ref import RuleRef


def _type_of(rule) -> object:
    return getattr(rule, "type", None)


def is_rule(rule) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule) -> bool:
    return _type_of(rule) == RuleType.REF


def is_rule_end(rule) -> bool:
    return _type_of(rule) == RuleType.END


def is_rule_char(rule) -> bool:
    return _type_of(rule) == RuleType.CHAR


def is_rule_char_exclude(rule) -> bool:
    return _type_of(rule) == RuleType.CHAR_EXCLUDE


def is_range(input) -> bool:
    return (
        isinstance(input, (list, tuple))
        and len(input) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in input)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_exclude(pointer.rule)


def is_resolved_rule(rule) -> bool:
    return is_rule_char(rule) or is_rule_char_exclude(rule) or is_rule_end(rule)
