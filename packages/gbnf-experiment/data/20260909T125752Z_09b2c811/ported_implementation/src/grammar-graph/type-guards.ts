import {
  Range,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  UnresolvedRule,
} from './grammar-graph-types.js';
import type { GraphPointer } from './graph-pointer.js';
import { RuleRef } from './rule-ref.js';

export const isRule = (rule: unknown): rule is UnresolvedRule =>
  rule !== null &&
  rule !== undefined &&
  (rule instanceof RuleChar ||
    rule instanceof RuleCharExclude ||
    rule instanceof RuleEnd ||
    rule instanceof RuleRef);

export const isRuleRef = (rule: unknown): rule is RuleRef =>
  rule instanceof RuleRef;

export const isRuleEnd = (rule: unknown): rule is RuleEnd =>
  rule instanceof RuleEnd;

export const isRuleChar = (rule: unknown): rule is RuleChar =>
  rule instanceof RuleChar;

export const isRuleCharExclude = (rule: unknown): rule is RuleCharExclude =>
  rule instanceof RuleCharExclude;

export const isRange = (input: unknown): input is Range =>
  Array.isArray(input) &&
  input.length === 2 &&
  input.every((n) => typeof n === 'number');

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
