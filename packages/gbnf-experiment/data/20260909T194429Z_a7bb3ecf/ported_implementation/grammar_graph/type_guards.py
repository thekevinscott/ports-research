from __future__ import annotations

from typing import Any, Optional

from .rule_ref import RuleRef
from .types import RuleType, UnresolvedRule, _Rule

"""Type Guards"""


def is_rule_type(type_: Any = None) -> bool:
    if not type_:
        return False
    try:
        return type_ in [t.value for t in RuleType]
    except TypeError:
        return False


def is_rule(rule: Any = None) -> bool:
    return isinstance(rule, _Rule) and is_rule_type(rule.type)


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.END


def is_rule_char(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.CHAR


def is_rule_char_excluded(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.CHAR_EXCLUDE


def is_range(range_: Any = None) -> bool:
    return (
        isinstance(range_, (list, tuple))
        and len(range_) == 2
        and all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in range_)
    )


def is_graph_pointer_rule_ref(pointer) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer) -> bool:
    return is_rule_char_excluded(pointer.rule)


# camelCase aliases mirroring the reference's exported names
isRuleType = is_rule_type
isRule = is_rule
isRuleRef = is_rule_ref
isRuleEnd = is_rule_end
isRuleChar = is_rule_char
isRuleCharExcluded = is_rule_char_excluded
isRange = is_range
