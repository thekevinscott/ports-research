from typing import Any

from .rule_ref import RuleRef
from .types import Rule, RuleChar, RuleCharExclude, RuleEnd, RuleType

"""Type Guards"""


def is_rule_type(type_: Any = None) -> bool:
    return bool(type_) and type_ in tuple(RuleType)


def is_rule(rule: Any = None) -> bool:
    if isinstance(rule, RuleRef):
        return True
    return isinstance(rule, Rule) and is_rule_type(getattr(rule, "type", None))


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


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_excluded(pointer.rule)
