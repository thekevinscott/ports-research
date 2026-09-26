import { RuleType } from './grammar-graph-types.ts';
import type { UnresolvedRule } from './grammar-graph-types.ts';
import {
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from './type-guards.ts';

const KEY_TRANSLATION: Record<RuleType, number> = {
  [RuleType.END]: 0,
  [RuleType.CHAR]: 1,
  [RuleType.CHAR_EXCLUDE]: 2,
  [RuleType.REF]: 3,
};

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
