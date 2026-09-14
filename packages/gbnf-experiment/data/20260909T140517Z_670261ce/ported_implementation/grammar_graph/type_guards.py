"""Port of ``src/grammar-graph/type-guards.ts``."""

from __future__ import annotations

from typing import Any

from .rule_ref import RuleRef
from .types import RuleChar, RuleCharExclude, RuleEnd, RuleType


def is_rule_type(type_: Any = None) -> bool:
    if not type_:
        return False
    try:
        RuleType(type_)
    except ValueError:
        return False
    return True


def is_rule(rule: Any = None) -> bool:
    if isinstance(rule, RuleRef):
        return True
    return isinstance(rule, (RuleChar, RuleCharExclude, RuleEnd)) and is_rule_type(rule.type)


def is_rule_ref(rule: Any = None) -> bool:
    return isinstance(rule, RuleRef)


def is_rule_end(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.END


def is_rule_char(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.CHAR


def is_rule_char_excluded(rule: Any = None) -> bool:
    return rule is not None and not is_rule_ref(rule) and rule.type == RuleType.CHAR_EXCLUDE


def is_range(rng: Any = None) -> bool:
    return (
        isinstance(rng, (list, tuple))
        and len(rng) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in rng)
    )


def is_graph_pointer_rule_ref(pointer: Any) -> bool:
    return is_rule_ref(pointer.rule)


def is_graph_pointer_rule_end(pointer: Any) -> bool:
    return is_rule_end(pointer.rule)


def is_graph_pointer_rule_char(pointer: Any) -> bool:
    return is_rule_char(pointer.rule)


def is_graph_pointer_rule_char_exclude(pointer: Any) -> bool:
    return is_rule_char_excluded(pointer.rule)


# Camel-cased aliases mirroring the reference export names.
isRange = is_range
isRule = is_rule
isRuleRef = is_rule_ref
isRuleEnd = is_rule_end
isRuleChar = is_rule_char
isRuleCharExcluded = is_rule_char_excluded
