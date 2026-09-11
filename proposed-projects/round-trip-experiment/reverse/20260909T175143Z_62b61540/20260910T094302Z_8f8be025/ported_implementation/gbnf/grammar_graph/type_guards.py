from typing import Any, Optional

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef


def is_rule(rule: Any) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: Optional[Any] = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Optional[Any] = None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Optional[Any] = None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_exclude(rule: Optional[Any] = None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(input_: Any) -> bool:
    return (
        isinstance(input_, list)
        and len(input_) == 2
        and all(isinstance(n, int) for n in input_)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_exclude(pointer.rule)
