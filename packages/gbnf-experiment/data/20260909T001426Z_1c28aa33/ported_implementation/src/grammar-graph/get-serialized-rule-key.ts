import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from './grammar-graph-types';
import {
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from './type-guards';

export const KEY_TRANSLATION = new Map<unknown, number>([
  [RuleEnd, 0],
  [RuleChar, 1],
  [RuleCharExclude, 2],
]);

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION.get(RuleEnd)}`;
  }

  if (isRuleChar(rule)) {
    return `${KEY_TRANSLATION.get(RuleChar)}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION.get(RuleCharExclude)}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${rule}`);
};
