from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef


def is_rule(rule) -> bool:
    return rule is not None and isinstance(
        rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef)
    )


def is_rule_ref(rule) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule) -> bool:
    return rule is not None and isinstance(rule, RuleEnd)


def is_rule_char(rule) -> bool:
    return rule is not None and isinstance(rule, RuleChar)


def is_rule_char_exclude(rule) -> bool:
    return rule is not None and isinstance(rule, RuleCharExclude)


def is_range(inpt) -> bool:
    return (
        isinstance(inpt, list)
        and len(inpt) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in inpt)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_exclude(pointer.rule)
