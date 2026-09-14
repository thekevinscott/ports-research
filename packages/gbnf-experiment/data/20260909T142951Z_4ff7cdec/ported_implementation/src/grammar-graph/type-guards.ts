import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from './grammar-graph-types.ts';
import type { Range, UnresolvedRule } from './grammar-graph-types.ts';
import type { GraphPointer } from './graph-pointer.ts';
import { RuleRef } from './rule-ref.ts';

export const isRule = (rule: unknown): rule is UnresolvedRule =>
  rule instanceof RuleChar ||
  rule instanceof RuleCharExclude ||
  rule instanceof RuleEnd ||
  rule instanceof RuleRef;

export const isRuleRef = (rule?: UnresolvedRule | null): rule is RuleRef =>
  rule?.type === RuleType.REF;

export const isRuleEnd = (rule?: UnresolvedRule | null): rule is RuleEnd =>
  rule?.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule | null): rule is RuleChar =>
  rule?.type === RuleType.CHAR;

export const isRuleCharExclude = (
  rule?: UnresolvedRule | null
): rule is RuleCharExclude => rule?.type === RuleType.CHAR_EXCLUDE;

export const isRange = (input: unknown): input is Range =>
  Array.isArray(input) &&
  input.length === 2 &&
  input.every(n => typeof n === 'number');

export const isGraphPointerRuleRef = (
  pointer: GraphPointer
): pointer is GraphPointer<RuleRef> => isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (
  pointer: GraphPointer
): pointer is GraphPointer<RuleEnd> => isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (
  pointer: GraphPointer
): pointer is GraphPointer<RuleChar> => isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (
  pointer: GraphPointer
): pointer is GraphPointer<RuleCharExclude> => isRuleCharExclude(pointer.rule);
