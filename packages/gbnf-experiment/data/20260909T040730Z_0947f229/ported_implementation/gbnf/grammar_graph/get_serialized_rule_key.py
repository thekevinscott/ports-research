"""Port of ``src/grammar-graph/get-serialized-rule-key.ts``."""

from __future__ import annotations

import json

from .type_guards import is_rule_char, is_rule_char_excluded, is_rule_end, is_rule_ref
from .types import RuleType, UnresolvedRule

KEY_TRANSLATION = {
    RuleType.END: 0,
    RuleType.CHAR: 1,
    RuleType.CHAR_EXCLUDE: 2,
}


def get_serialized_rule_key(rule: UnresolvedRule) -> str:
    if is_rule_end(rule):
        return f'{KEY_TRANSLATION[RuleType.END]}'

    if is_rule_char(rule) or is_rule_char_excluded(rule):
        value = json.dumps(rule.value, separators=(',', ':'))
        return f'{KEY_TRANSLATION[rule.type]}-{value}'

    if is_rule_ref(rule):
        return f'3-{rule.value}'

    raise ValueError(f'Unknown rule type: {rule!r}')
