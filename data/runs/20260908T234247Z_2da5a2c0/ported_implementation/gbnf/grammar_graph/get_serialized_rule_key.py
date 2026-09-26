"""Port of ``src/grammar-graph/get-serialized-rule-key.ts``."""

from __future__ import annotations

import json
from typing import Any

from .type_guards import is_rule_char, is_rule_char_excluded, is_rule_end, is_rule_ref
from .types import RuleType

KEY_TRANSLATION = {
    RuleType.END: 0,
    RuleType.CHAR: 1,
    RuleType.CHAR_EXCLUDE: 2,
}


def get_serialized_rule_key(rule: Any) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION[RuleType.END]}"

    if is_rule_char(rule) or is_rule_char_excluded(rule):
        return (
            f"{KEY_TRANSLATION[rule.type]}-"
            f"{json.dumps(rule.value, separators=(',', ':'))}"
        )
    if is_rule_ref(rule):
        return f"3-{rule.value}"
    raise ValueError(f"Unknown rule type: {rule!r}")
