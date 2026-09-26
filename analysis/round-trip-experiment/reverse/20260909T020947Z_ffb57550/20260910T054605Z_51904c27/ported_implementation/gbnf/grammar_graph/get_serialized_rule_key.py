import json
from typing import Any

from .rule_type import RuleType
from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref

KEY_TRANSLATION = {
    RuleType.END: 0,
    RuleType.CHAR: 1,
    RuleType.CHAR_EXCLUDE: 2,
    RuleType.REF: 3,
}


def get_serialized_rule_key(rule: Any) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION[RuleType.END]}"

    if is_rule_char(rule):
        return f"{KEY_TRANSLATION[RuleType.CHAR]}-{json.dumps(rule.value)}"

    if is_rule_char_exclude(rule):
        return f"{KEY_TRANSLATION[RuleType.CHAR_EXCLUDE]}-{json.dumps(rule.value)}"

    if is_rule_ref(rule):
        return f"{KEY_TRANSLATION[RuleType.REF]}-{rule.value}"

    raise ValueError(f"Unknown rule type: {rule!r}")
