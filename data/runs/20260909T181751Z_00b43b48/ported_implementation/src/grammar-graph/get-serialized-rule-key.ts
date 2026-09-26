import type { UnresolvedRule } from './grammar-graph-types.js';
import { isRuleChar, isRuleCharExclude, isRuleEnd, isRuleRef } from './type-guards.js';

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return '0';
  }

  if (isRuleChar(rule)) {
    return `1-${JSON.stringify(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `2-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${JSON.stringify(rule)}`);
};
