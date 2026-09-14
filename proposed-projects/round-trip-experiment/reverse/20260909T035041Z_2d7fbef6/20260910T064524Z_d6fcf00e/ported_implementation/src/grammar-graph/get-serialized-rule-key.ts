import { GBNFError } from '../utils/errors/gbnf-error.js';
import { isRuleChar, isRuleCharExcluded, isRuleEnd, isRuleRef } from './type-guards.js';
import { RuleType, UnresolvedRule } from './types.js';

export const KEY_TRANSLATION = {
  [RuleType.END]: 0,
  [RuleType.CHAR]: 1,
  [RuleType.CHAR_EXCLUDE]: 2,
} as const;

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

  throw new GBNFError(`Unknown rule type: ${rule}`);
};
