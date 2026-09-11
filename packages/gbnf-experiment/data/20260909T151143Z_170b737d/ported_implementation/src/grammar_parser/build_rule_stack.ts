import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type UnresolvedRule,
} from "../grammar_graph/grammar_graph_types.ts";
import { RuleRef } from "../grammar_graph/rule_ref.ts";
import { is_range, is_rule_end } from "../grammar_graph/type_guards.ts";
import { json_dumps } from "../utils/python_compat.ts";
import {
  is_rule_def_alt,
  is_rule_def_char,
  is_rule_def_char_alt,
  is_rule_def_char_not,
  is_rule_def_char_rng_upper,
  is_rule_def_end,
  is_rule_def_ref,
  type InternalRuleDef,
  type InternalRuleDefChar,
  type InternalRuleDefCharNot,
} from "../rules_builder/rules_builder_types.ts";

export const make_char_rule = (
  rule_def: InternalRuleDefChar | InternalRuleDefCharNot,
): RuleChar | RuleCharExclude => {
  const value = rule_def.value as Array<number | Range>;
  if (is_rule_def_char_not(rule_def)) {
    return new RuleCharExclude(value);
  }
  if (is_rule_def_char(rule_def)) {
    return new RuleChar(value);
  }

  throw new Error(`Unsupported rule type for make_char_rule: ${rule_def}`);
};

export const build_rule_stack = (linear_rules: InternalRuleDef[]): UnresolvedRule[][] => {
  let paths: UnresolvedRule[] = [];
  const stack: UnresolvedRule[][] = [];
  let idx = 0;

  while (idx < linear_rules.length) {
    const rule_def = linear_rules[idx];
    if (is_rule_def_char(rule_def) || is_rule_def_char_not(rule_def)) {
      // this could be a single char, or a range, or a sequence of alts; we don't know until we step through it.
      const char_rule = make_char_rule(rule_def);
      idx += 1;
      let rule: InternalRuleDef | null = idx < linear_rules.length ? linear_rules[idx] : null;
      while (
        idx < linear_rules.length &&
        (is_rule_def_char_rng_upper(rule) || is_rule_def_char_alt(rule))
      ) {
        if (is_rule_def_char_rng_upper(rule)) {
          // previous rule value should be a number
          const prev_value = char_rule.value.pop();
          if (is_range(prev_value)) {
            throw new Error(
              `Unexpected range, expected a number but got an array: ${json_dumps(prev_value)}`,
            );
          }
          if (prev_value === undefined) {
            throw new Error("Unexpected undefined value");
          }

          char_rule.value.push([prev_value as number, rule.value]);
        }
        if (is_rule_def_char_alt(rule)) {
          char_rule.value.push(rule.value);
        }
        idx += 1;
        rule = idx < linear_rules.length ? linear_rules[idx] : null;
      }
      paths.push(char_rule);
    } else {
      if (is_rule_def_alt(rule_def)) {
        if (paths.length === 0) {
          throw new Error("Encountered alt without anything before it");
        }
        paths.push(new RuleEnd());
        stack.push(paths);
        paths = [];
      } else if (is_rule_def_end(rule_def)) {
        paths.push(new RuleEnd());
      } else if (is_rule_def_ref(rule_def)) {
        paths.push(new RuleRef(rule_def.value));
      } else if (is_rule_def_char_alt(rule_def)) {
        throw new Error(`Encountered char alt, should be handled by above block: ${rule_def}`);
      } else {
        throw new Error(`Unsupported rule type: ${rule_def}`);
      }
      idx += 1;
    }
  }

  if (!is_rule_end(paths[paths.length - 1])) {
    paths.push(new RuleEnd());
  }

  stack.push(paths);
  return stack;
};
