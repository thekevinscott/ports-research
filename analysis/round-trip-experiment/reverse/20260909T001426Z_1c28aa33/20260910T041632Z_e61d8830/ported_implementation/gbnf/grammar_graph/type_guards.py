from typing import Any, Optional

from .grammar_graph_types import Rule, RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef


def is_rule(rule: Any) -> bool:
    return isinstance(rule, (Rule, RuleRef))


def is_rule_ref(rule: Optional[Any]) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Optional[Any]) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Optional[Any]) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_exclude(rule: Optional[Any]) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(input: Any) -> bool:
    return (
        isinstance(input, (list, tuple))
        and len(input) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in input)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_exclude(pointer.rule)
