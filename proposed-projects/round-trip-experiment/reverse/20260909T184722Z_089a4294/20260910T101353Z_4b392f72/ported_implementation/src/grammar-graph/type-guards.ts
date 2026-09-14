import { RuleRef } from './rule-ref';
import { RuleChar, RuleCharExclude, RuleEnd, RuleType } from './types';
import type { Range } from './types';
import type { GraphPointer } from './graph-pointer';

export const isRuleType = (type: unknown): boolean =>
  Boolean(type) && Object.values(RuleType).includes(type as RuleType);

export const isRule = (rule: unknown): boolean =>
  rule instanceof RuleChar ||
  rule instanceof RuleCharExclude ||
  rule instanceof RuleEnd ||
  rule instanceof RuleRef;

export const isRuleRef = (rule: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRuleEnd = (rule: unknown): rule is RuleEnd => rule instanceof RuleEnd;

export const isRuleChar = (rule: unknown): rule is RuleChar => rule instanceof RuleChar;

export const isRuleCharExcluded = (rule: unknown): rule is RuleCharExclude =>
  rule instanceof RuleCharExclude;

export const isRange = (rng: unknown): rng is Range =>
  Array.isArray(rng) && rng.length === 2 && rng.every(n => typeof n === 'number');

export const isGraphPointerRuleRef = (pointer: GraphPointer): boolean =>
  isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): boolean =>
  isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: GraphPointer): boolean =>
  isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: GraphPointer): boolean =>
  isRuleCharExcluded(pointer.rule);
