from typing import Any

from .rule_ref import RuleRef
from .types import RuleChar, RuleCharExclude, RuleEnd, RuleType


def is_rule_type(type_: Any = None) -> bool:
    return bool(type_) and type_ in set(RuleType)


def is_rule(rule: Any = None) -> bool:
    return rule is not None and (
        isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))
    )


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any = None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Any = None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_excluded(rule: Any = None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(range_: Any = None) -> bool:
    return (
        isinstance(range_, (list, tuple))
        and len(range_) == 2
        and all(isinstance(n, int) for n in range_)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_excluded(pointer.rule)
