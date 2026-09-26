from __future__ import annotations

import json

from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref
from .types import RuleType

KEY_TRANSLATION = {
    RuleType.END: 0,
    RuleType.CHAR: 1,
    RuleType.CHAR_EXCLUDE: 2,
    RuleType.REF: 3,
}


def _stringify(value) -> str:
    return json.dumps(value, separators=(',', ':'))


def get_serialized_rule_key(rule) -> str:
    if is_rule_end(rule):
        return f'{KEY_TRANSLATION[RuleType.END]}'

    if is_rule_char(rule):
        return f'{KEY_TRANSLATION[RuleType.CHAR]}-{_stringify(rule.value)}'

    if is_rule_char_exclude(rule):
        return f'{KEY_TRANSLATION[RuleType.CHAR_EXCLUDE]}-{_stringify(rule.value)}'

    if is_rule_ref(rule):
        return f'{KEY_TRANSLATION[RuleType.REF]}-{rule.value}'

    raise ValueError(f'Unknown rule type: {rule!r}')
