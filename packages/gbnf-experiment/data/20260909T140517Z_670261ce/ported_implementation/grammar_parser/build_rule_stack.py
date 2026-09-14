"""Port of ``src/grammar-parser/build-rule-stack.ts``."""

from __future__ import annotations

from typing import Any, List

from ..grammar_graph.rule_ref import RuleRef
from ..grammar_graph.type_guards import is_range, is_rule_end
from ..grammar_graph.types import RuleChar, RuleCharExclude, RuleEnd
from ..rules_builder.type_guards import (
    is_rule_def_alt,
    is_rule_def_char,
    is_rule_def_char_alt,
    is_rule_def_char_not,
    is_rule_def_char_rng_upper,
    is_rule_def_end,
    is_rule_def_ref,
)
from ..rules_builder.types import InternalRuleDef
from ..utils.js import last


def make_char_rule(rule_def: InternalRuleDef) -> Any:
    if is_rule_def_char_not(rule_def):
        return RuleCharExclude(value=list(rule_def.value))
    return RuleChar(value=list(rule_def.value))


def build_rule_stack(linear_rules: List[InternalRuleDef]) -> List[List[Any]]:
    paths: List[Any] = []

    stack: List[List[Any]] = []

    idx = 0
    while idx < len(linear_rules):
        rule_def = linear_rules[idx]
        if is_rule_def_char(rule_def) or is_rule_def_char_not(rule_def):
            # this could be a single char, or a range, or a sequence of alts; we don't
            # know until we step through it.
            char_rule = make_char_rule(rule_def)
            idx += 1
            rule = linear_rules[idx] if idx < len(linear_rules) else None
            while idx < len(linear_rules) and (
                is_rule_def_char_rng_upper(rule) or is_rule_def_char_alt(rule)
            ):
                if is_rule_def_char_rng_upper(rule):
                    # previous rule value should be a number
                    prev_value = char_rule.value.pop() if char_rule.value else None
                    if is_range(prev_value):
                        raise ValueError(
                            "Unexpected range, expected a number but got an array: "
                            f"{prev_value!r}"
                        )
                    if prev_value is None:
                        raise ValueError("Unexpected undefined value")
                    char_rule.value.append([prev_value, rule.value])
                if is_rule_def_char_alt(rule):
                    char_rule.value.append(rule.value)
                idx += 1
                rule = linear_rules[idx] if idx < len(linear_rules) else None
            paths.append(char_rule)
        else:
            if is_rule_def_alt(rule_def):
                if not paths:
                    raise ValueError("Encountered alt without anything before it")
                paths.append(RuleEnd())
                stack.append(paths)
                paths = []
            elif is_rule_def_end(rule_def):
                paths.append(RuleEnd())
            elif is_rule_def_ref(rule_def):
                paths.append(RuleRef(rule_def.value))
            elif is_rule_def_char_alt(rule_def):
                raise ValueError(
                    "Encountered char alt, should be handled by above block: "
                    f"{rule_def.type.value}"
                )
            else:
                raise ValueError(f"Unsupported rule type: {rule_def.type.value}")
            idx += 1

    if not is_rule_end(last(paths)):
        paths.append(RuleEnd())

    stack.append(paths)

    return stack


buildRuleStack = build_rule_stack
