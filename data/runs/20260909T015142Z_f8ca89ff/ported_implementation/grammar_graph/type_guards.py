from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .rule_ref import RuleRef
from .types import Rule, RuleType

if TYPE_CHECKING:  # pragma: no cover
    from .graph_pointer import GraphPointer

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
    # camelCase aliases, matching the reference API
    "isRuleType",
    "isRule",
    "isRuleRef",
    "isRuleEnd",
    "isRuleChar",
    "isRuleCharExcluded",
    "isRange",
]

_RULE_TYPE_VALUES = {member.value for member in RuleType}


def _type_of(rule: Any) -> Any:
    if isinstance(rule, dict):
        return rule.get("type")
    return getattr(rule, "type", None)


def is_rule_type(type_: Any = None) -> bool:
    if not type_:
        return False
    if isinstance(type_, RuleType):
        return True
    return type_ in _RULE_TYPE_VALUES


def is_rule(rule: Any = None) -> bool:
    if not rule:
        return False
    if isinstance(rule, Rule):
        return True
    if isinstance(rule, dict):
        return "type" in rule and is_rule_type(rule["type"])
    return hasattr(rule, "type") and is_rule_type(rule.type)


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and _type_of(rule) == RuleType.END


def is_rule_char(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and _type_of(rule) == RuleType.CHAR


def is_rule_char_excluded(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and _type_of(rule) == RuleType.CHAR_EXCLUDE


def is_range(rng: Any = None) -> bool:
    return (
        isinstance(rng, (list, tuple))
        and len(rng) == 2
        and all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in rng)
    )


def is_graph_pointer_rule_ref(pointer: "GraphPointer") -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: "GraphPointer") -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: "GraphPointer") -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: "GraphPointer") -> bool:
    return is_rule_char_excluded(pointer.rule)


isRuleType = is_rule_type
isRule = is_rule
isRuleRef = is_rule_ref
isRuleEnd = is_rule_end
isRuleChar = is_rule_char
isRuleCharExcluded = is_rule_char_excluded
isRange = is_range
isGraphPointerRuleRef = is_graph_pointer_rule_ref
isGraphPointerRuleEnd = is_graph_pointer_rule_end
isGraphPointerRuleChar = is_graph_pointer_rule_char
isGraphPointerRuleCharExclude = is_graph_pointer_rule_char_exclude
