import type { UnresolvedRule } from './grammar-graph-types.js';
import {
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from './type-guards.js';

const KEY_TRANSLATION = {
  RuleEnd: 0,
  RuleChar: 1,
  RuleCharExclude: 2,
} as const;

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION.RuleEnd}`;
  }

  if (isRuleChar(rule)) {
    return `${KEY_TRANSLATION.RuleChar}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION.RuleCharExclude}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${rule}`);
};
