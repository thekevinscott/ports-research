/** Type guards mirroring the reference implementation's `type_guards.py`. */

import type { GraphPointer } from './graph-pointer.js';
import { RuleRef } from './rule-ref.js';
import {
  Range,
  ResolvedRule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from './types.js';

const RULE_TYPE_VALUES = new Set<string>(Object.values(RuleType));

export type Rule = ResolvedRule | RuleRef;

export const isRuleType = (type?: unknown): type is RuleType =>
  !!type && typeof type === 'string' && RULE_TYPE_VALUES.has(type);

export const isRule = (rule?: unknown): rule is Rule =>
  rule !== undefined &&
  rule !== null &&
  (rule instanceof RuleRef ||
    isRuleType((rule as { type?: unknown }).type));

export const isRuleRef = (rule?: unknown): rule is RuleRef =>
  rule instanceof RuleRef;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd =>
  rule !== undefined &&
  rule !== null &&
  !isRuleRef(rule) &&
  (rule as ResolvedRule).type === RuleType.END;

export const isRuleChar = (rule?: unknown): rule is RuleChar =>
  rule !== undefined &&
  rule !== null &&
  !isRuleRef(rule) &&
  (rule as ResolvedRule).type === RuleType.CHAR;

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  rule !== undefined &&
  rule !== null &&
  !isRuleRef(rule) &&
  (rule as ResolvedRule).type === RuleType.CHAR_EXCLUDE;

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) &&
  range.length === 2 &&
  range.every((n) => typeof n === 'number');

export const isGraphPointerRuleRef = (pointer: GraphPointer): boolean =>
  isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): boolean =>
  isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: GraphPointer): boolean =>
  isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (
  pointer: GraphPointer,
): boolean => isRuleCharExcluded(pointer.rule);
