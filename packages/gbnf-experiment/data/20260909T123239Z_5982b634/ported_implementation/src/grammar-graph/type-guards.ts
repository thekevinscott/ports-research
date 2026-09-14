import type { GraphPointer } from './graph-pointer.js';
import { RuleRef } from './rule-ref.js';
import {
  RuleType,
  type Range,
  type RuleChar,
  type RuleCharExclude,
  type RuleEnd,
  type UnresolvedRule,
} from './types.js';

export const isRule = (rule?: unknown): rule is UnresolvedRule =>
  rule instanceof RuleRef ||
  (typeof rule === 'object' &&
    rule !== null &&
    Object.values(RuleType).includes((rule as UnresolvedRule).type));

export const isRuleRef = (rule?: UnresolvedRule): rule is RuleRef =>
  rule?.type === RuleType.REF;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd =>
  rule?.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar =>
  rule?.type === RuleType.CHAR;

export const isRuleCharExclude = (rule?: UnresolvedRule): rule is RuleCharExclude =>
  rule?.type === RuleType.CHAR_EXCLUDE;

export const isRange = (input?: number | Range): input is Range =>
  Array.isArray(input) && input.length === 2 && input.every(Number.isInteger);

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
