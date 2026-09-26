from typing import Any

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef


def is_rule(rule: Any) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: Any) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Any) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_exclude(rule: Any) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(input_: Any) -> bool:
    return (
        isinstance(input_, list)
        and len(input_) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in input_)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_exclude(pointer.rule)
