import json
from typing import Optional, Union

from ..grammar_graph.grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from ..grammar_graph.rule_ref import RuleRef
from ..grammar_graph.type_guards import is_range, is_rule_end
from ..rules_builder.rules_builder_types import (
    InternalRuleDef,
    is_rule_def_alt,
    is_rule_def_char,
    is_rule_def_char_alt,
    is_rule_def_char_not,
    is_rule_def_char_rng_upper,
    is_rule_def_end,
    is_rule_def_ref,
)


def _serialize(rule_def: InternalRuleDef) -> str:
    return json.dumps(rule_def, separators=(",", ":"), default=str)


def _at(rules: list[InternalRuleDef], idx: int) -> Optional[InternalRuleDef]:
    if 0 <= idx < len(rules):
        return rules[idx]
    return None


def make_char_rule(rule_def: InternalRuleDef) -> Union[RuleChar, RuleCharExclude]:
    if is_rule_def_char_not(rule_def):
        return RuleCharExclude(rule_def["value"])
    if is_rule_def_char(rule_def):
        return RuleChar(rule_def["value"])

    raise ValueError(
        f"Unsupported rule type for make_char_rule: {_serialize(rule_def)}"
    )


def build_rule_stack(linear_rules: list[InternalRuleDef]) -> list[list]:
    paths: list = []
    stack: list[list] = []
    idx = 0

    while idx < len(linear_rules):
        rule_def = linear_rules[idx]
        if is_rule_def_char(rule_def) or is_rule_def_char_not(rule_def):
            # this could be a single char, or a range, or a sequence of alts;
            # we don't know until we step through it.
            char_rule = make_char_rule(rule_def)
            idx += 1
            rule = _at(linear_rules, idx)
            while idx < len(linear_rules) and (
                is_rule_def_char_rng_upper(rule) or is_rule_def_char_alt(rule)
            ):
                if is_rule_def_char_rng_upper(rule):
                    # previous rule value should be a number
                    prev_value = char_rule.value.pop() if char_rule.value else None
                    if is_range(prev_value):
                        raise ValueError(
                            "Unexpected range, expected a number but got an array: "
                            f"{json.dumps(prev_value, separators=(',', ':'))}"
                        )
                    if prev_value is None:
                        raise ValueError("Unexpected undefined value")

                    char_rule.value.append([prev_value, rule["value"]])
                if is_rule_def_char_alt(rule):
                    char_rule.value.append(rule["value"])
                idx += 1
                rule = _at(linear_rules, idx)
            paths.append(char_rule)
        else:
            if is_rule_def_alt(rule_def):
                if len(paths) == 0:
                    raise ValueError("Encountered alt without anything before it")
                paths.append(RuleEnd())
                stack.append(paths)
                paths = []
            elif is_rule_def_end(rule_def):
                paths.append(RuleEnd())
            elif is_rule_def_ref(rule_def):
                paths.append(RuleRef(rule_def["value"]))
            elif is_rule_def_char_alt(rule_def):
                raise ValueError(
                    "Encountered char alt, should be handled by above block: "
                    f"{_serialize(rule_def)}"
                )
            else:
                raise ValueError(f"Unsupported rule type: {_serialize(rule_def)}")
            idx += 1

    if not is_rule_end(paths[-1] if paths else None):
        paths.append(RuleEnd())

    stack.append(paths)
    return stack
