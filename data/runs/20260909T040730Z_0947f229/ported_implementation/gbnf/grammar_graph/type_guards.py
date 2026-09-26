"""Port of ``src/grammar-graph/type-guards.ts``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .rule_ref import RuleRef
from .types import RuleChar, RuleCharExclude, RuleEnd, RuleType, UnresolvedRule

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_pointer import GraphPointer


def is_rule_type(type: object = None) -> bool:
    return isinstance(type, RuleType)


def is_rule(rule: object = None) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_excluded(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(range: object = None) -> bool:
    return (
        isinstance(range, (list, tuple))
        and len(range) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in range)
    )


def is_graph_pointer_rule_ref(pointer: 'GraphPointer') -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: 'GraphPointer') -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: 'GraphPointer') -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: 'GraphPointer') -> bool:
    return is_rule_char_excluded(pointer.rule)
