import { isRuleChar, isRuleCharExcluded, isRuleEnd, isRuleRef } from './type-guards.js';
import type { UnresolvedRule } from './type-guards.js';
import { type RuleCharValue, RuleType } from './types.js';

const KEY_TRANSLATION: Record<RuleType, number> = {
  [RuleType.END]: 0,
  [RuleType.CHAR]: 1,
  [RuleType.CHAR_EXCLUDE]: 2,
};

/** e.g. `[97,[98,99]]` */
export const serializeValue = (value: RuleCharValue[]): string => JSON.stringify(value);

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION[RuleType.END]}`;
  }

  if (isRuleChar(rule) || isRuleCharExcluded(rule)) {
    return `${KEY_TRANSLATION[rule.type]}-${serializeValue(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${JSON.stringify(rule)}`);
};
