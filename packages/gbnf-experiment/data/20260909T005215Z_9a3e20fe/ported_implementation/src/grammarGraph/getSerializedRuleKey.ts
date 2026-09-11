import { jsonDumps, repr } from '../utils/repr.ts';
import { RuleChar, RuleCharExclude, RuleEnd } from './grammarGraphTypes.ts';
import type { UnresolvedRule } from './grammarGraphTypes.ts';
import { isRuleChar, isRuleCharExclude, isRuleEnd, isRuleRef } from './typeGuards.ts';

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
    return `${KEY_TRANSLATION.get(RuleChar)}-${jsonDumps(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION.get(RuleCharExclude)}-${jsonDumps(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${repr(rule)}`);
};
