from typing import Any

from .rule_type import RuleType


def _type_of(rule: Any) -> Any:
    return getattr(rule, "type", None)


def is_rule(rule: Any) -> bool:
    return _type_of(rule) in (
        RuleType.CHAR,
        RuleType.CHAR_EXCLUDE,
        RuleType.END,
        RuleType.REF,
    )


def is_rule_ref(rule: Any = None) -> bool:
    return _type_of(rule) == RuleType.REF


def is_rule_end(rule: Any = None) -> bool:
    return _type_of(rule) == RuleType.END


def is_rule_char(rule: Any = None) -> bool:
    return _type_of(rule) == RuleType.CHAR


def is_rule_char_exclude(rule: Any = None) -> bool:
    return _type_of(rule) == RuleType.CHAR_EXCLUDE


def is_range(input: Any) -> bool:
    return (
        isinstance(input, list)
        and len(input) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in input)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_exclude(pointer.rule)
