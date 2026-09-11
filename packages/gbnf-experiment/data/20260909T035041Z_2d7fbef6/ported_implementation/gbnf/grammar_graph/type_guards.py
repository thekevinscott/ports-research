from __future__ import annotations

from .rule_ref import RuleRef
from .types import Rule, RuleChar, RuleCharExclude, RuleEnd, RuleType


def is_rule_type(type=None) -> bool:
    if not type:
        return False
    if isinstance(type, RuleType):
        return True
    return type in {member.value for member in RuleType}


def is_rule(rule=None) -> bool:
    return isinstance(rule, Rule) and is_rule_type(rule.type)


def is_rule_ref(rule=None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule=None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule=None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_excluded(rule=None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(range_=None) -> bool:
    return (
        isinstance(range_, (list, tuple))
        and len(range_) == 2
        and all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in range_)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_excluded(pointer.rule)
