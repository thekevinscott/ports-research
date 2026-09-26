from __future__ import annotations

from typing import Any

from .rule_ref import RuleRef
from .types import Rule, RuleChar, RuleCharExclude, RuleEnd, RuleType


def is_rule_type(type: Any = None) -> bool:
    return isinstance(type, RuleType)


def is_rule(rule: Any = None) -> bool:
    return isinstance(rule, (Rule, RuleRef))


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any = None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Any = None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_excluded(rule: Any = None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(range: Any = None) -> bool:
    return (
        isinstance(range, (list, tuple))
        and len(range) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in range)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_excluded(pointer.rule)
