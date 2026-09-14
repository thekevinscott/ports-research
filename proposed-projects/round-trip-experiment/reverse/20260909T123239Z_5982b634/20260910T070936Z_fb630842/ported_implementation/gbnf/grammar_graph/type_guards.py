from __future__ import annotations

from typing import Any, Optional

from .rule_ref import RuleRef
from .types import RuleType


def is_rule(rule: Optional[Any] = None) -> bool:
    if isinstance(rule, RuleRef):
        return True
    return rule is not None and getattr(rule, 'type', None) in tuple(RuleType)


def is_rule_ref(rule: Optional[Any] = None) -> bool:
    return rule is not None and getattr(rule, 'type', None) == RuleType.REF


def is_rule_end(rule: Optional[Any] = None) -> bool:
    return rule is not None and getattr(rule, 'type', None) == RuleType.END


def is_rule_char(rule: Optional[Any] = None) -> bool:
    return rule is not None and getattr(rule, 'type', None) == RuleType.CHAR


def is_rule_char_exclude(rule: Optional[Any] = None) -> bool:
    return rule is not None and getattr(rule, 'type', None) == RuleType.CHAR_EXCLUDE


def is_range(input: Optional[Any] = None) -> bool:
    return (
        isinstance(input, list)
        and len(input) == 2
        and all(isinstance(i, int) and not isinstance(i, bool) for i in input)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_exclude(pointer.rule)
