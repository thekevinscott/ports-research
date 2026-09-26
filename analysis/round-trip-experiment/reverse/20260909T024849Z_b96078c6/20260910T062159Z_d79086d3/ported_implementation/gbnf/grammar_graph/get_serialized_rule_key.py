from __future__ import annotations

import json

from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref

KEY_TRANSLATION = {
    "RuleEnd": 0,
    "RuleChar": 1,
    "RuleCharExclude": 2,
}


def _serialize(value: object) -> str:
    return json.dumps(value, separators=(",", ":"))


def get_serialized_rule_key(rule: object) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION['RuleEnd']}"

    if is_rule_char(rule):
        return f"{KEY_TRANSLATION['RuleChar']}-{_serialize(rule.value)}"

    if is_rule_char_exclude(rule):
        return f"{KEY_TRANSLATION['RuleCharExclude']}-{_serialize(rule.value)}"

    if is_rule_ref(rule):
        return f"3-{rule.value}"

    raise ValueError(f"Unknown rule type: {rule}")
