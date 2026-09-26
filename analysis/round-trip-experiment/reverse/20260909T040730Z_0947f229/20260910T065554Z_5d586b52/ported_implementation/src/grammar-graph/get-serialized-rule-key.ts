/** Port of `gbnf/grammar_graph/get_serialized_rule_key.py`. */

import { isRuleChar, isRuleCharExcluded, isRuleEnd, isRuleRef } from './type-guards.js';
import { RuleType, UnresolvedRule } from './types.js';

const KEY_TRANSLATION: Record<RuleType, number> = {
  [RuleType.END]: 0,
  [RuleType.CHAR]: 1,
  [RuleType.CHAR_EXCLUDE]: 2,
};

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION[RuleType.END]}`;
  }

  if (isRuleChar(rule) || isRuleCharExcluded(rule)) {
    return `${KEY_TRANSLATION[rule.type]}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${JSON.stringify(rule)}`);
};
