from __future__ import annotations

from typing import Any

from ..utils.js_compat import json_stringify
from .type_guards import is_rule_char, is_rule_char_excluded, is_rule_end, is_rule_ref
from .types import RuleType

__all__ = ["KEY_TRANSLATION", "get_serialized_rule_key", "getSerializedRuleKey"]

KEY_TRANSLATION = {
    RuleType.END: 0,
    RuleType.CHAR: 1,
    RuleType.CHAR_EXCLUDE: 2,
}


def get_serialized_rule_key(rule: Any) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION[RuleType.END]}"

    if is_rule_char(rule) or is_rule_char_excluded(rule):
        value = [list(v) if isinstance(v, (list, tuple)) else v for v in rule.value]
        return f"{KEY_TRANSLATION[rule.type]}-{json_stringify(value)}"

    if is_rule_ref(rule):
        return f"3-{rule.value}"

    raise Exception(f"Unknown rule type: {rule!r}")


getSerializedRuleKey = get_serialized_rule_key
