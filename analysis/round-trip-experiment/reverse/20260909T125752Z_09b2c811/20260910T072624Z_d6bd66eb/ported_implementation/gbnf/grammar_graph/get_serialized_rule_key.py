"""Serialize a rule to a key, so identical rules can share a single instance."""

import json
from typing import Any

from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref


class KEY_TRANSLATION:
    RuleEnd = 0
    RuleChar = 1
    RuleCharExclude = 2
    RuleRef = 3


def _serialize_value(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"))


def get_serialized_rule_key(rule: Any) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION.RuleEnd}"

    if is_rule_char(rule):
        return f"{KEY_TRANSLATION.RuleChar}-{_serialize_value(rule.value)}"

    if is_rule_char_exclude(rule):
        return f"{KEY_TRANSLATION.RuleCharExclude}-{_serialize_value(rule.value)}"

    if is_rule_ref(rule):
        return f"{KEY_TRANSLATION.RuleRef}-{rule.value}"

    raise ValueError(f"Unknown rule type: {rule}")
