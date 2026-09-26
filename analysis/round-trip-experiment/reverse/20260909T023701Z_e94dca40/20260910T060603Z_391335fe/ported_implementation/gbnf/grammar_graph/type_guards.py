from __future__ import annotations

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef


def is_rule(rule: object) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: object | None = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: object | None = None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: object | None = None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_exclude(rule: object | None = None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in value)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_exclude(pointer.rule)
