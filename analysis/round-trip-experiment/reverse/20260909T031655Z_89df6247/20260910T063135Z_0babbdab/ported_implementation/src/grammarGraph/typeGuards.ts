import { RuleRef } from './ruleRef.js';
import {
  BaseRule,
  RULE_TYPES,
  Range,
  Rule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from './types.js';
import type { GraphPointer } from './graphPointer.js';

export type GraphRule = Rule | RuleRef;

export const isRuleType = (type?: unknown): type is RuleType =>
  Boolean(type) && RULE_TYPES.includes(type as RuleType);

export const isRule = (rule?: unknown): rule is GraphRule =>
  (rule instanceof BaseRule || rule instanceof RuleRef) &&
  (rule instanceof RuleRef || isRuleType(rule.type));

export const isRuleRef = (rule?: unknown): rule is RuleRef =>
  rule instanceof RuleRef;

export const isRuleEnd = (rule?: GraphRule | null): rule is RuleEnd =>
  rule !== undefined &&
  rule !== null &&
  !isRuleRef(rule) &&
  rule.type === RuleType.END;

export const isRuleChar = (rule?: GraphRule | null): rule is RuleChar =>
  rule !== undefined &&
  rule !== null &&
  !isRuleRef(rule) &&
  rule.type === RuleType.CHAR;

export const isRuleCharExcluded = (
  rule?: GraphRule | null
): rule is RuleCharExclude =>
  rule !== undefined &&
  rule !== null &&
  !isRuleRef(rule) &&
  rule.type === RuleType.CHAR_EXCLUDE;

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

export const isGraphPointerRuleCharExclude = (pointer: GraphPointer): boolean =>
  isRuleCharExcluded(pointer.rule);
