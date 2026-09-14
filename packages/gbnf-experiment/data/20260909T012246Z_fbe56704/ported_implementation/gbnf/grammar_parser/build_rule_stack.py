from typing import List, Optional, Union

from ..grammar_graph.rule_ref import RuleRef
from ..grammar_graph.type_guards import is_range, is_rule_end
from ..grammar_graph.types import (
    Range,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    UnresolvedRule,
)
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


def build_rule_stack(
    linear_rules: Optional[List[InternalRuleDef]],
) -> List[List[UnresolvedRule]]:
    # a rule id that was never defined shows up as a hole in the reference
    # implementation's rules array; treat it as an empty rule.
    if linear_rules is None:
        linear_rules = []

    paths: List[UnresolvedRule] = []
    stack: List[List[UnresolvedRule]] = []

    idx = 0
    while idx < len(linear_rules):
        rule_def = linear_rules[idx]
        if is_rule_def_char(rule_def) or is_rule_def_char_not(rule_def):
            # this could be a single char, or a range, or a sequence of alts; we don't
            # know until we step through it.
            is_exclude = is_rule_def_char_not(rule_def)
            values: List[Union[int, Range]] = list(rule_def.value)
            idx += 1
            rule = linear_rules[idx] if idx < len(linear_rules) else None
            while idx < len(linear_rules) and (
                is_rule_def_char_rng_upper(rule) or is_rule_def_char_alt(rule)
            ):
                if is_rule_def_char_rng_upper(rule):
                    # previous rule value should be a number
                    prev_value = values.pop() if values else None
                    if is_range(prev_value):
                        raise ValueError(
                            "Unexpected range, expected a number but got a list: "
                            f"{prev_value!r}"
                        )
                    if prev_value is None:
                        raise ValueError("Unexpected undefined value")
                    values.append((prev_value, rule.value))
                if is_rule_def_char_alt(rule):
                    values.append(rule.value)
                idx += 1
                rule = linear_rules[idx] if idx < len(linear_rules) else None
            paths.append(RuleCharExclude(values) if is_exclude else RuleChar(values))
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
                    f"{rule_def.type}"
                )
            else:
                raise ValueError(f"Unsupported rule type: {rule_def.type}")
            idx += 1

    if not is_rule_end(paths[-1] if paths else None):
        paths.append(RuleEnd())

    stack.append(paths)

    return stack
