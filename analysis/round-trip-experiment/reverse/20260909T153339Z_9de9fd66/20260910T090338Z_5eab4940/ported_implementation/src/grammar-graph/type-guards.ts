import { RuleRef } from './rule-ref.js';
import {
  RuleType,
  type Range,
  type Rule,
  type RuleChar,
  type RuleCharExclude,
  type RuleEnd,
  type UnresolvedRule,
} from './types.js';

/** Type Guards */

const RULE_TYPES = new Set<string>(Object.values(RuleType));

export const isRuleType = (type?: unknown): type is RuleType =>
  typeof type === 'string' && RULE_TYPES.has(type);

export const isRule = (rule?: unknown): rule is UnresolvedRule => {
  if (rule instanceof RuleRef) {
    return true;
  }
  return (
    typeof rule === 'object' && rule !== null && isRuleType((rule as Rule).type)
  );
};

export const isRuleRef = (rule?: UnresolvedRule): rule is RuleRef =>
  rule instanceof RuleRef;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd =>
  !!rule && !(rule instanceof RuleRef) && rule.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar =>
  !!rule && !(rule instanceof RuleRef) && rule.type === RuleType.CHAR;

export const isRuleCharExcluded = (
  rule?: UnresolvedRule
): rule is RuleCharExclude =>
  !!rule && !(rule instanceof RuleRef) && rule.type === RuleType.CHAR_EXCLUDE;

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) &&
  range.length === 2 &&
  range.every((n) => typeof n === 'number');
