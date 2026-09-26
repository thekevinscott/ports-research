import { json_dumps } from "../utils/python_compat.ts";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from "./grammar_graph_types.ts";
import { RuleRef } from "./rule_ref.ts";
import { is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref } from "./type_guards.ts";

export const KEY_TRANSLATION = new Map<unknown, number>([
  [RuleEnd, 0],
  [RuleChar, 1],
  [RuleCharExclude, 2],
]);

export const get_serialized_rule_key = (rule: UnresolvedRule): string => {
  if (is_rule_end(rule)) {
    return `${KEY_TRANSLATION.get(RuleEnd)}`;
  }

  if (is_rule_char(rule)) {
    return `${KEY_TRANSLATION.get(RuleChar)}-${json_dumps(rule.value)}`;
  }

  if (is_rule_char_exclude(rule)) {
    return `${KEY_TRANSLATION.get(RuleCharExclude)}-${json_dumps(rule.value)}`;
  }

  if (is_rule_ref(rule)) {
    return `3-${(rule as RuleRef).value}`;
  }

  throw new Error(`Unknown rule type: ${rule}`);
};
