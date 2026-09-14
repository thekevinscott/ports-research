import { RuleRef } from './rule-ref.ts';
import { RuleChar, RuleCharExclude, RuleEnd, RuleType } from './types.ts';
import type { Range, UnresolvedRule } from './types.ts';
import type { GraphPointer } from './graph-pointer.ts';

const RULE_TYPES = new Set<unknown>(Object.values(RuleType));

export const isRuleType = (ruleType?: unknown): ruleType is RuleType =>
  !!ruleType && RULE_TYPES.has(ruleType);

export const isRule = (rule?: unknown): rule is UnresolvedRule =>
  rule instanceof RuleChar ||
  rule instanceof RuleCharExclude ||
  rule instanceof RuleEnd ||
  rule instanceof RuleRef;

export const isRuleRef = (rule?: UnresolvedRule): rule is RuleRef =>
  rule instanceof RuleRef;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd =>
  rule instanceof RuleEnd;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar =>
  rule instanceof RuleChar;

export const isRuleCharExcluded = (rule?: UnresolvedRule): rule is RuleCharExclude =>
  rule instanceof RuleCharExclude;

export const isRange = (value?: unknown): value is Range =>
  Array.isArray(value) &&
  value.length === 2 &&
  value.every((n) => typeof n === 'number');

export const isGraphPointerRuleRef = (pointer: GraphPointer): boolean =>
  isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): boolean =>
  isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: GraphPointer): boolean =>
  isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: GraphPointer): boolean =>
  isRuleCharExcluded(pointer.rule);
