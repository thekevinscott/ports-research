import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type UnresolvedRule,
} from './grammar_graph_types.ts';
import { RuleRef } from './rule_ref.ts';

import type { GraphPointer } from './graph_pointer.ts';

export const isRule = (rule: unknown): rule is UnresolvedRule =>
  rule !== null &&
  rule !== undefined &&
  (rule instanceof RuleChar ||
    rule instanceof RuleCharExclude ||
    rule instanceof RuleEnd ||
    rule instanceof RuleRef);

export const isRuleRef = (rule: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRuleEnd = (rule: unknown): rule is RuleEnd => rule instanceof RuleEnd;

export const isRuleChar = (rule: unknown): rule is RuleChar => rule instanceof RuleChar;

export const isRuleCharExclude = (rule: unknown): rule is RuleCharExclude =>
  rule instanceof RuleCharExclude;

export const isRange = (input: unknown): input is Range =>
  Array.isArray(input) && input.length === 2 && input.every((n) => Number.isInteger(n));

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

export const is_rule = isRule;
export const is_rule_ref = isRuleRef;
export const is_rule_end = isRuleEnd;
export const is_rule_char = isRuleChar;
export const is_rule_char_exclude = isRuleCharExclude;
export const is_range = isRange;
export const is_graph_pointer_rule_ref = isGraphPointerRuleRef;
export const is_graph_pointer_rule_end = isGraphPointerRuleEnd;
export const is_graph_pointer_rule_char = isGraphPointerRuleChar;
export const is_graph_pointer_rule_char_exclude = isGraphPointerRuleCharExclude;
