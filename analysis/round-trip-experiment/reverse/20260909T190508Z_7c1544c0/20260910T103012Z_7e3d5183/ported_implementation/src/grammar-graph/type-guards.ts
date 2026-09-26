import { RuleRef } from './rule-ref.js';
import {
  Range,
  ResolvedRule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from './types.js';

export type UnresolvedRule = ResolvedRule | RuleRef;

const RULE_TYPES = new Set<string>(Object.values(RuleType));

export const isRuleType = (type?: unknown): boolean =>
  Boolean(type) && typeof type === 'string' && RULE_TYPES.has(type);

export const isRule = (rule?: unknown): rule is UnresolvedRule =>
  isRuleRef(rule) ||
  (typeof rule === 'object' &&
    rule !== null &&
    isRuleType((rule as ResolvedRule).type));

export const isRuleRef = (rule?: unknown): rule is RuleRef =>
  rule instanceof RuleRef;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd =>
  !isRuleRef(rule) &&
  typeof rule === 'object' &&
  rule !== null &&
  (rule as ResolvedRule).type === RuleType.END;

export const isRuleChar = (rule?: unknown): rule is RuleChar =>
  !isRuleRef(rule) &&
  typeof rule === 'object' &&
  rule !== null &&
  (rule as ResolvedRule).type === RuleType.CHAR;

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  !isRuleRef(rule) &&
  typeof rule === 'object' &&
  rule !== null &&
  (rule as ResolvedRule).type === RuleType.CHAR_EXCLUDE;

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) &&
  range.length === 2 &&
  range.every((n) => typeof n === 'number');

export const isGraphPointerRuleRef = (pointer: {
  rule: UnresolvedRule;
}): boolean => isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: {
  rule: UnresolvedRule;
}): boolean => isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: {
  rule: UnresolvedRule;
}): boolean => isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: {
  rule: UnresolvedRule;
}): boolean => isRuleCharExcluded(pointer.rule);
