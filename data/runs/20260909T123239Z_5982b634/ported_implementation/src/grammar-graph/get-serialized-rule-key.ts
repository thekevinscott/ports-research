import { isRuleChar, isRuleCharExclude, isRuleEnd, isRuleRef } from './type-guards.js';
import { RuleType, type UnresolvedRule } from './types.js';

const KEY_TRANSLATION = {
  [RuleType.END]: 0,
  [RuleType.CHAR]: 1,
  [RuleType.CHAR_EXCLUDE]: 2,
  [RuleType.REF]: 3,
} as const;

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION[RuleType.END]}`;
  }

  if (isRuleChar(rule)) {
    return `${KEY_TRANSLATION[RuleType.CHAR]}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION[RuleType.CHAR_EXCLUDE]}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `${KEY_TRANSLATION[RuleType.REF]}-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${JSON.stringify(rule)}`);
};
