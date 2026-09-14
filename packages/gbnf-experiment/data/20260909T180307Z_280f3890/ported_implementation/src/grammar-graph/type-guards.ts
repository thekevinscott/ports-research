import {
  type Range,
  type ResolvedRule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
  type UnresolvedRule,
} from './grammar-graph-types.js';
import type { GraphPointer } from './graph-pointer.js';
import { RuleRef } from './rule-ref.js';

export const isRule = (rule: unknown): rule is UnresolvedRule =>
  rule instanceof RuleChar ||
  rule instanceof RuleCharExclude ||
  rule instanceof RuleEnd ||
  rule instanceof RuleRef;

export const isRuleRef = (rule?: UnresolvedRule): rule is RuleRef => rule?.type === RuleType.REF;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd => rule?.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar => rule?.type === RuleType.CHAR;

export const isRuleCharExclude = (rule?: UnresolvedRule): rule is RuleCharExclude =>
  rule?.type === RuleType.CHAR_EXCLUDE;

export const isRange = (input: unknown): input is Range =>
  Array.isArray(input) && input.length === 2 && input.every(n => Number.isInteger(n));

export const isGraphPointerRuleRef = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleRef> => isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleEnd> => isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleChar> => isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleCharExclude> => isRuleCharExclude(pointer.rule);

export const isResolvedRule = (rule?: UnresolvedRule): rule is ResolvedRule =>
  isRuleChar(rule) || isRuleCharExclude(rule) || isRuleEnd(rule);
