import type { GraphPointer } from './graph-pointer.js';
import {
  Range,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
  UnresolvedRule,
} from './grammar-graph-types.js';
import type { RuleRef } from './rule-ref.js';

export const isRule = (rule?: unknown): rule is UnresolvedRule => (
  rule instanceof RuleChar
  || rule instanceof RuleCharExclude
  || rule instanceof RuleEnd
  || (!!rule && (rule as UnresolvedRule).type === RuleType.REF)
);

export const isRuleRef = (rule?: UnresolvedRule): rule is RuleRef => rule?.type === RuleType.REF;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd => rule?.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar => rule?.type === RuleType.CHAR;

export const isRuleCharExclude = (rule?: UnresolvedRule): rule is RuleCharExclude => (
  rule?.type === RuleType.CHAR_EXCLUDE
);

export const isRange = (input?: unknown): input is Range => (
  Array.isArray(input) && input.length === 2 && input.every(n => typeof n === 'number')
);

export const isGraphPointerRuleRef = (pointer: GraphPointer): pointer is GraphPointer<RuleRef> => (
  isRuleRef(pointer.rule)
);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): pointer is GraphPointer<RuleEnd> => (
  isRuleEnd(pointer.rule)
);

export const isGraphPointerRuleChar = (pointer: GraphPointer): pointer is GraphPointer<RuleChar> => (
  isRuleChar(pointer.rule)
);

export const isGraphPointerRuleCharExclude = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleCharExclude> => isRuleCharExclude(pointer.rule);
