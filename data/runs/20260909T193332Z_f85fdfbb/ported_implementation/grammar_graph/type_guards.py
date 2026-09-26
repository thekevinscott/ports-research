from __future__ import annotations

from typing import Any

from .rule_ref import RuleRef
from .types import Rule, RuleType

__all__ = [
    "is_rule_type",
    "is_rule",
    "is_rule_ref",
    "is_rule_end",
    "is_rule_char",
    "is_rule_char_excluded",
    "is_range",
    "is_graph_pointer_rule_ref",
    "is_graph_pointer_rule_end",
    "is_graph_pointer_rule_char",
    "is_graph_pointer_rule_char_exclude",
]


def is_rule_type(type_: Any = None) -> bool:
    if not type_:
        return False
    return type_ in tuple(RuleType)


def is_rule(rule: Any = None) -> bool:
    if isinstance(rule, (Rule, RuleRef)):
        return True
    if isinstance(rule, dict) and "type" in rule:
        return is_rule_type(rule["type"])
    return False


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any = None) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and getattr(rule, "type", None) == RuleType.END
    )


def is_rule_char(rule: Any = None) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and getattr(rule, "type", None) == RuleType.CHAR
    )


def is_rule_char_excluded(rule: Any = None) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and getattr(rule, "type", None) == RuleType.CHAR_EXCLUDE
    )


def is_range(rng: Any = None) -> bool:
    return (
        isinstance(rng, (list, tuple))
        and len(rng) == 2
        and all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in rng)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_excluded(pointer.rule)
