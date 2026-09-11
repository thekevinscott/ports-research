import type { UnresolvedRule } from './grammar-graph-types.js';
import {
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from './type-guards.js';

const KEY_TRANSLATION = {
  END: 0,
  CHAR: 1,
  CHAR_EXCLUDE: 2,
  REF: 3,
} as const;

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION.END}`;
  }

  if (isRuleChar(rule)) {
    return `${KEY_TRANSLATION.CHAR}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION.CHAR_EXCLUDE}-${JSON.stringify(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `${KEY_TRANSLATION.REF}-${rule.value}`;
  }

  throw new Error(`Unknown rule type: ${String(rule)}`);
};
