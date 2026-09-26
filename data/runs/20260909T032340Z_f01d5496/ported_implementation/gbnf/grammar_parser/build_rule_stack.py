from typing import List, Optional, Union

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

UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]


def _make_char_rule(rule_def) -> Union[RuleChar, RuleCharExclude]:
    cls = RuleCharExclude if is_rule_def_char_not(rule_def) else RuleChar
    return cls(list(rule_def.value))


def build_rule_stack(linear_rules) -> Optional[List[List[UnresolvedRule]]]:
    if linear_rules is None:
        # the reference implementation's rules array can be sparse; holes map through
        # untouched.
        return None

    paths: List[UnresolvedRule] = []
    stack: List[List[UnresolvedRule]] = []

    idx = 0
    while idx < len(linear_rules):
        rule_def = linear_rules[idx]
        if is_rule_def_char(rule_def) or is_rule_def_char_not(rule_def):
            # this could be a single char, or a range, or a sequence of alts; we don't
            # know until we step through it.
            char_rule = _make_char_rule(rule_def)
            idx += 1
            rule = linear_rules[idx] if idx < len(linear_rules) else None
            while idx < len(linear_rules) and (
                is_rule_def_char_rng_upper(rule) or is_rule_def_char_alt(rule)
            ):
                if is_rule_def_char_rng_upper(rule):
                    # previous rule value should be a number
                    if not char_rule.value:
                        raise Exception("Unexpected undefined value")
                    prev_value = char_rule.value.pop()
                    if is_range(prev_value):
                        raise Exception(
                            "Unexpected range, expected a number but got an array: "
                            f"{prev_value}"
                        )
                    char_rule.value.append([prev_value, rule.value])
                if is_rule_def_char_alt(rule):
                    char_rule.value.append(rule.value)
                idx += 1
                rule = linear_rules[idx] if idx < len(linear_rules) else None
            paths.append(char_rule)
        else:
            if is_rule_def_alt(rule_def):
                if not paths:
                    raise Exception("Encountered alt without anything before it")
                paths.append(RuleEnd())
                stack.append(paths)
                paths = []
            elif is_rule_def_end(rule_def):
                paths.append(RuleEnd())
            elif is_rule_def_ref(rule_def):
                paths.append(RuleRef(rule_def.value))
            elif is_rule_def_char_alt(rule_def):
                raise Exception(
                    "Encountered char alt, should be handled by above block: "
                    f"{rule_def.type}"
                )
            else:
                raise Exception(f"Unsupported rule type: {rule_def.type}")
            idx += 1

    if not paths or not is_rule_end(paths[-1]):
        paths.append(RuleEnd())

    stack.append(paths)

    return stack
