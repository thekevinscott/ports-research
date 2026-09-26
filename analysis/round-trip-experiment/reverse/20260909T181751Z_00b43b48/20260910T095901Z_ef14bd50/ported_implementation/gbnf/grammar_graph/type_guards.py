from typing import TYPE_CHECKING, Any, Optional

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd, RuleType

if TYPE_CHECKING:
    from .graph_pointer import GraphPointer
    from .grammar_graph_types import UnresolvedRule


def is_rule(rule: Any = None) -> bool:
    return (
        isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd))
        or (rule is not None and getattr(rule, "type", None) == RuleType.REF)
    )


def is_rule_ref(rule: Optional["UnresolvedRule"] = None) -> bool:
    return getattr(rule, "type", None) == RuleType.REF


def is_rule_end(rule: Optional["UnresolvedRule"] = None) -> bool:
    return getattr(rule, "type", None) == RuleType.END


def is_rule_char(rule: Optional["UnresolvedRule"] = None) -> bool:
    return getattr(rule, "type", None) == RuleType.CHAR


def is_rule_char_exclude(rule: Optional["UnresolvedRule"] = None) -> bool:
    return getattr(rule, "type", None) == RuleType.CHAR_EXCLUDE


def is_range(input: Any = None) -> bool:
    return (
        isinstance(input, (list, tuple))
        and len(input) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in input)
    )


def is_graph_pointer_rule_ref(pointer: "GraphPointer") -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: "GraphPointer") -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: "GraphPointer") -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: "GraphPointer") -> bool:
    return is_rule_char_exclude(pointer.rule)
