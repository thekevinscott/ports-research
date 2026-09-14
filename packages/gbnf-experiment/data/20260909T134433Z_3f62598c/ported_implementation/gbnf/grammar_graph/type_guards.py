from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .rule_ref import RuleRef
from .types import RuleChar, RuleCharExclude, RuleEnd, RuleType

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_pointer import GraphPointer


def is_rule_type(type_: Any = None) -> bool:
    if isinstance(type_, RuleType):
        return True
    return isinstance(type_, str) and type_ in {t.value for t in RuleType}


def is_rule(rule: Any = None) -> bool:
    return rule is not None and (
        isinstance(rule, RuleRef)
        or (hasattr(rule, "type") and is_rule_type(rule.type))
    )


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any = None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Any = None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_excluded(rule: Any = None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(rng: Any = None) -> bool:
    return (
        isinstance(rng, (list, tuple))
        and len(rng) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in rng)
    )


def is_graph_pointer_rule_ref(pointer: "GraphPointer") -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: "GraphPointer") -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: "GraphPointer") -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: "GraphPointer") -> bool:
    return is_rule_char_excluded(pointer.rule)


