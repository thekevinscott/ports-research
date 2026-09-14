"""Port of ``src/grammar-graph/type-guards.ts``."""

from __future__ import annotations

from typing import Any

from .rule_ref import RuleRef
from .types import RuleChar, RuleCharExclude, RuleEnd, RuleType


def is_rule_type(type: Any = None) -> bool:
    if not type:
        return False
    try:
        return RuleType(type) in RuleType
    except ValueError:
        return False


def is_rule(rule: Any = None) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def _rule_type(rule: Any) -> Any:
    """`rule.type` in JS is `undefined` for anything that isn't a rule, never an error."""
    return getattr(rule, "type", None)


def is_rule_end(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and _rule_type(rule) == RuleType.END


def is_rule_char(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and _rule_type(rule) == RuleType.CHAR


def is_rule_char_excluded(rule: Any = None) -> bool:
    return (
        rule is not None
        and not is_rule_ref(rule)
        and _rule_type(rule) == RuleType.CHAR_EXCLUDE
    )


def is_range(rng: Any = None) -> bool:
    return (
        isinstance(rng, (list, tuple))
        and len(rng) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in rng)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_excluded(pointer.rule)
