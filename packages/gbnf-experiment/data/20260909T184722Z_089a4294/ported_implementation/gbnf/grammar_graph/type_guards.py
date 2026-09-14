from __future__ import annotations

from .rule_ref import RuleRef
from .types import RuleChar, RuleCharExclude, RuleEnd, RuleType


def is_rule_type(type_: object) -> bool:
    return bool(type_) and type_ in tuple(RuleType)


def is_rule(rule: object) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: object) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: object) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: object) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_excluded(rule: object) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(rng: object) -> bool:
    return (
        isinstance(rng, (list, tuple))
        and len(rng) == 2
        and all(isinstance(n, int) for n in rng)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_excluded(pointer.rule)
