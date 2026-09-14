import { RuleChar, RuleCharExclude, RuleEnd, type UnresolvedRule } from './grammar-graph-types.ts';
import { isRuleChar, isRuleCharExclude, isRuleEnd, isRuleRef } from './type-guards.ts';

export const KEY_TRANSLATION = {
  [RuleEnd.name]: 0,
  [RuleChar.name]: 1,
  [RuleCharExclude.name]: 2,
} as const;

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION[RuleEnd.name]}`;
  }

  if (isRuleChar(rule)) {
    return `${KEY_TRANSLATION[RuleChar.name]}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION[RuleCharExclude.name]}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${rule}`);
};
