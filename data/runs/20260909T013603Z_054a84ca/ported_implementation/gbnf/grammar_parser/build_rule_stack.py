from __future__ import annotations

from typing import List, Sequence, Union

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
from ..utils.js import at

UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd, RuleRef]


def make_char_rule(rule_def: InternalRuleDef) -> Union[RuleChar, RuleCharExclude]:
    cls = RuleCharExclude if is_rule_def_char_not(rule_def) else RuleChar
    return cls(list(rule_def.value))


def build_rule_stack(linear_rules: Sequence[InternalRuleDef]) -> List[List[UnresolvedRule]]:
    paths: List[UnresolvedRule] = []

    stack: List[List[UnresolvedRule]] = []

    idx = 0
    while idx < len(linear_rules):
        rule_def = linear_rules[idx]
        if is_rule_def_char(rule_def) or is_rule_def_char_not(rule_def):
            # this could be a single char, or a range, or a sequence of alts; we don't
            # know until we step through it.
            char_rule = make_char_rule(rule_def)
            idx += 1
            rule = at(linear_rules, idx)
            while idx < len(linear_rules) and (
                is_rule_def_char_rng_upper(rule) or is_rule_def_char_alt(rule)
            ):
                if is_rule_def_char_rng_upper(rule):
                    # previous rule value should be a number
                    prev_value = char_rule.value.pop() if char_rule.value else None
                    if is_range(prev_value):
                        raise ValueError(
                            f'Unexpected range, expected a number but got an array: {prev_value}'
                        )
                    if prev_value is None:
                        raise ValueError('Unexpected undefined value')
                    char_rule.value.append([prev_value, rule.value])
                if is_rule_def_char_alt(rule):
                    char_rule.value.append(rule.value)
                idx += 1
                rule = at(linear_rules, idx)
            paths.append(char_rule)
        else:
            if is_rule_def_alt(rule_def):
                if not paths:
                    raise ValueError('Encountered alt without anything before it')
                paths.append(RuleEnd())
                stack.append(paths)
                paths = []
            elif is_rule_def_end(rule_def):
                paths.append(RuleEnd())
            elif is_rule_def_ref(rule_def):
                paths.append(RuleRef(rule_def.value))
            elif is_rule_def_char_alt(rule_def):
                raise ValueError(
                    f'Encountered char alt, should be handled by above block: {rule_def.type}'
                )
            else:
                raise ValueError(f'Unsupported rule type: {rule_def.type}')
            idx += 1

    if not is_rule_end(at(paths, len(paths) - 1)):
        paths.append(RuleEnd())

    stack.append(paths)

    return stack
