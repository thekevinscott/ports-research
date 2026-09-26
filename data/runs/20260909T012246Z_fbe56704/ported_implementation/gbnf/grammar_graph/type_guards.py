from typing import Any, Optional

from .rule_ref import RuleRef
from .types import RuleChar, RuleCharExclude, RuleEnd, RuleType, UnresolvedRule


def is_rule_type(rule_type: Any = None) -> bool:
    return bool(rule_type) and rule_type in tuple(RuleType)


def is_rule(rule: Any = None) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def is_rule_ref(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleEnd)


def is_rule_char(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleChar)


def is_rule_char_excluded(rule: Optional[UnresolvedRule] = None) -> bool:
    return isinstance(rule, RuleCharExclude)


def is_range(value: Any = None) -> bool:
    return (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(n, int) for n in value)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_excluded(pointer.rule)
