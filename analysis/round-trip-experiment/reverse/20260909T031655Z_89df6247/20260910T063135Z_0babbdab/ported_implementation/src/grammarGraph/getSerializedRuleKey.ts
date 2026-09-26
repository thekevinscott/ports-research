import {
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
  type GraphRule,
} from './typeGuards.js';
import { RuleType } from './types.js';

const KEY_TRANSLATION: Record<RuleType, number> = {
  [RuleType.END]: 0,
  [RuleType.CHAR]: 1,
  [RuleType.CHAR_EXCLUDE]: 2,
};

export const getSerializedRuleKey = (rule: GraphRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION[RuleType.END]}`;
  }

  if (isRuleChar(rule) || isRuleCharExcluded(rule)) {
    return `${KEY_TRANSLATION[rule.type]}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${JSON.stringify(rule)}`);
};
