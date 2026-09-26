import { RuleRef } from './rule-ref';
import { Range, RuleChar, RuleCharExclude, RuleEnd, RuleType } from './types';

const RULE_TYPES = new Set<string>(Object.values(RuleType));

export const isRuleType = (type?: unknown): type is RuleType =>
  typeof type === 'string' && RULE_TYPES.has(type);

export const isRule = (rule?: unknown): boolean =>
  rule instanceof RuleChar ||
  rule instanceof RuleCharExclude ||
  rule instanceof RuleEnd ||
  rule instanceof RuleRef;

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd => rule instanceof RuleEnd;

export const isRuleChar = (rule?: unknown): rule is RuleChar => rule instanceof RuleChar;

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  rule instanceof RuleCharExclude;

export const isRange = (rng?: unknown): rng is Range =>
  Array.isArray(rng) &&
  rng.length === 2 &&
  rng.every((n) => typeof n === 'number' && Number.isInteger(n));

export const isGraphPointerRuleRef = (pointer: { rule: unknown }): boolean =>
  isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: { rule: unknown }): boolean =>
  isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: { rule: unknown }): boolean =>
  isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: { rule: unknown }): boolean =>
  isRuleCharExcluded(pointer.rule);
