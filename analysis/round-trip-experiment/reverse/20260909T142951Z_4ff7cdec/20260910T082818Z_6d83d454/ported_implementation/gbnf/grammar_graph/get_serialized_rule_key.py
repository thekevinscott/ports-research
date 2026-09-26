from typing import Any

from .grammar_graph_types import RuleType
from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref

KEY_TRANSLATION = {
    RuleType.END: 0,
    RuleType.CHAR: 1,
    RuleType.CHAR_EXCLUDE: 2,
    RuleType.REF: 3,
}


def _serialize_value(value: Any) -> str:
    return "[" + ",".join(
        f"[{v[0]},{v[1]}]" if isinstance(v, (list, tuple)) else str(v) for v in value
    ) + "]"


def get_serialized_rule_key(rule: Any) -> str:
    if is_rule_end(rule):
        return f"{KEY_TRANSLATION[RuleType.END]}"

    if is_rule_char(rule):
        return f"{KEY_TRANSLATION[RuleType.CHAR]}-{_serialize_value(rule.value)}"

    if is_rule_char_exclude(rule):
        return (
            f"{KEY_TRANSLATION[RuleType.CHAR_EXCLUDE]}-{_serialize_value(rule.value)}"
        )

    if is_rule_ref(rule):
        return f"{KEY_TRANSLATION[RuleType.REF]}-{rule.value}"

    raise ValueError(f"Unknown rule type: {rule!r}")
