from __future__ import annotations

from .grammar_graph_types import Rule, RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef


def is_rule(rule: object) -> bool:
    return rule is not None and isinstance(
        rule,
        (RuleChar, RuleCharExclude, RuleEnd, RuleRef),
    )


def is_rule_ref(rule: object) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: object) -> bool:
    return rule is not None and isinstance(rule, RuleEnd)


def is_rule_char(rule: object) -> bool:
    return rule is not None and isinstance(rule, RuleChar)


def is_rule_char_exclude(rule: object) -> bool:
    return rule is not None and isinstance(rule, RuleCharExclude)


def is_range(input_: object) -> bool:
    return (
        isinstance(input_, (list, tuple))
        and len(input_) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in input_)
    )


def is_graph_pointer_rule_ref(pointer: object) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: object) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: object) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: object) -> bool:
    return is_rule_char_exclude(pointer.rule)


def is_rule_instance(rule: object) -> bool:
    """Mirrors the base class check; exported for completeness."""
    return isinstance(rule, Rule)
