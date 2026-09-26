import json
from typing import TYPE_CHECKING

from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref

if TYPE_CHECKING:
    from .grammar_graph_types import UnresolvedRule


def get_serialized_rule_key(rule: "UnresolvedRule") -> str:
    if is_rule_end(rule):
        return "0"

    if is_rule_char(rule):
        return f"1-{json.dumps(rule.value)}"

    if is_rule_char_exclude(rule):
        return f"2-{json.dumps(rule.value)}"

    if is_rule_ref(rule):
        return f"3-{rule.value}"

    raise Exception(f"Unknown rule type: {rule!r}")
