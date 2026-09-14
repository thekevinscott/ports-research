import json
from typing import Any

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref

KEY_TRANSLATION = {
    RuleEnd.__name__: 0,
    RuleChar.__name__: 1,
    RuleCharExclude.__name__: 2,
}


def get_serialized_rule_key(rule: Any) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION[RuleEnd.__name__]}"

    if is_rule_char(rule):
        return f"{KEY_TRANSLATION[RuleChar.__name__]}-{json.dumps(rule.value)}"

    if is_rule_char_exclude(rule):
        return f"{KEY_TRANSLATION[RuleCharExclude.__name__]}-{json.dumps(rule.value)}"

    if is_rule_ref(rule):
        return f"3-{rule.value}"

    raise Exception(f"Unknown rule type: {rule}")
