import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type UnresolvedRule,
} from "./grammar_graph_types.ts";
import { RuleRef } from "./rule_ref.ts";
import type { GraphPointer } from "./graph_pointer.ts";

export const is_rule = (rule: unknown): rule is UnresolvedRule =>
  rule !== null &&
  rule !== undefined &&
  (rule instanceof RuleChar ||
    rule instanceof RuleCharExclude ||
    rule instanceof RuleEnd ||
    rule instanceof RuleRef);

export const is_rule_ref = (rule: unknown): rule is RuleRef => rule instanceof RuleRef;

export const is_rule_end = (rule: unknown): rule is RuleEnd =>
  rule !== null && rule !== undefined && rule instanceof RuleEnd;

export const is_rule_char = (rule: unknown): rule is RuleChar =>
  rule !== null && rule !== undefined && rule instanceof RuleChar;

export const is_rule_char_exclude = (rule: unknown): rule is RuleCharExclude =>
  rule !== null && rule !== undefined && rule instanceof RuleCharExclude;

export const is_range = (inpt: unknown): inpt is Range =>
  Array.isArray(inpt) && inpt.length === 2 && inpt.every((n) => Number.isInteger(n));

export const is_graph_pointer_rule_ref = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleRef> => is_rule_ref(pointer.rule);

export const is_graph_pointer_rule_end = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleEnd> => is_rule_end(pointer.rule);

export const is_graph_pointer_rule_char = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleChar> => is_rule_char(pointer.rule);

export const is_graph_pointer_rule_char_exclude = (
  pointer: GraphPointer,
): pointer is GraphPointer<RuleCharExclude> => is_rule_char_exclude(pointer.rule);
