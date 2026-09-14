import json

from .grammar_graph_types import UnresolvedRule
from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref


class KEY_TRANSLATION:
    END = 0
    CHAR = 1
    CHAR_EXCLUDE = 2
    REF = 3


def get_serialized_rule_key(rule: UnresolvedRule) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION.END}"

    if is_rule_char(rule):
        return f"{KEY_TRANSLATION.CHAR}-{json.dumps(rule.value)}"

    if is_rule_char_exclude(rule):
        return f"{KEY_TRANSLATION.CHAR_EXCLUDE}-{json.dumps(rule.value)}"

    if is_rule_ref(rule):
        return f"{KEY_TRANSLATION.REF}-{rule.value}"

    raise ValueError(f"Unknown rule type: {rule}")
