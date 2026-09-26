from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef


def is_rule(rule: object) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: object) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: object) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: object) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_exclude(rule: object) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(input: object) -> bool:
    return (
        isinstance(input, list)
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
