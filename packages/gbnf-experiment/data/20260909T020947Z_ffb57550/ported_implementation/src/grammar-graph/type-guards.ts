import type {
  Range,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  UnresolvedRule,
} from './grammar-graph-types.js';
import type { GraphPointer } from './graph-pointer.js';
import type { RuleRef } from './rule-ref.js';
import { RuleType } from './rule-type.js';

export const isRule = (rule: unknown): rule is UnresolvedRule =>
  typeof rule === 'object' &&
  rule !== null &&
  'type' in rule &&
  [
    RuleType.CHAR,
    RuleType.CHAR_EXCLUDE,
    RuleType.END,
    RuleType.REF,
  ].includes((rule as UnresolvedRule).type);

export const isRuleRef = (rule?: UnresolvedRule): rule is RuleRef =>
  rule?.type === RuleType.REF;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd =>
  rule?.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar =>
  rule?.type === RuleType.CHAR;

export const isRuleCharExclude = (
  rule?: UnresolvedRule,
): rule is RuleCharExclude => rule?.type === RuleType.CHAR_EXCLUDE;

export const isRange = (input: unknown): input is Range =>
  Array.isArray(input) &&
  input.length === 2 &&
  input.every((n) => Number.isInteger(n));

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
