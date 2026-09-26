import type { UnresolvedRule } from './grammar-graph-types.js';
import { isRuleChar, isRuleCharExclude, isRuleEnd, isRuleRef } from './type-guards.js';

export const KEY_TRANSLATION = {
  end: 0,
  char: 1,
  char_exclude: 2,
  ref: 3,
} as const;

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION.end}`;
  }

  if (isRuleChar(rule)) {
    return `${KEY_TRANSLATION.char}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION.char_exclude}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `${KEY_TRANSLATION.ref}-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${JSON.stringify(rule)}`);
};
