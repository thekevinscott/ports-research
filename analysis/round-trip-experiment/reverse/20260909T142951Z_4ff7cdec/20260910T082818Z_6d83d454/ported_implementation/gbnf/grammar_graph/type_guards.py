from typing import Any, Optional

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd, RuleType
from .rule_ref import RuleRef


def is_rule(rule: Any) -> bool:
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd, RuleRef))


def _type_of(rule: Optional[Any]) -> Optional[str]:
    return getattr(rule, "type", None)


def is_rule_ref(rule: Optional[Any]) -> bool:
    return _type_of(rule) == RuleType.REF


def is_rule_end(rule: Optional[Any]) -> bool:
    return _type_of(rule) == RuleType.END


def is_rule_char(rule: Optional[Any]) -> bool:
    return _type_of(rule) == RuleType.CHAR


def is_rule_char_exclude(rule: Optional[Any]) -> bool:
    return _type_of(rule) == RuleType.CHAR_EXCLUDE


def is_range(input_: Any) -> bool:
    return (
        isinstance(input_, (list, tuple))
        and len(input_) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in input_)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_exclude(pointer.rule)
