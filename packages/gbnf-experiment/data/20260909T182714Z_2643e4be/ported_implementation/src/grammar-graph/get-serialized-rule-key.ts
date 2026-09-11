import { ValueError } from "../utils/errors/python-errors.js";
import type { Range, UnresolvedRule } from "./grammar-graph-types.js";
import {
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from "./type-guards.js";

const KEY_TRANSLATION = {
  RuleEnd: 0,
  RuleChar: 1,
  RuleCharExclude: 2,
} as const;

// Matches the spacing of Python's `json.dumps`, which the reference uses here.
const dumps = (value: (number | Range)[]): string =>
  `[${value
    .map((v) => (Array.isArray(v) ? `[${v.join(", ")}]` : `${v}`))
    .join(", ")}]`;

export const getSerializedRuleKey = (rule: UnresolvedRule): string => {
  if (isRuleEnd(rule)) {
    return `${KEY_TRANSLATION.RuleEnd}`;
  }

  if (isRuleChar(rule)) {
    return `${KEY_TRANSLATION.RuleChar}-${dumps(rule.value)}`;
  }

  if (isRuleCharExclude(rule)) {
    return `${KEY_TRANSLATION.RuleCharExclude}-${dumps(rule.value)}`;
  }

  if (isRuleRef(rule)) {
    return `3-${rule.value}`;
  }

  throw new ValueError(`Unknown rule type: ${String(rule)}`);
};
