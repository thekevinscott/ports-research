import { RuleRef } from './rule-ref.js';
import {
  Range,
  Rule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from './types.js';
import type { GraphPointer } from './graph-pointer.js';

const RULE_TYPES: string[] = [
  RuleType.CHAR,
  RuleType.CHAR_EXCLUDE,
  RuleType.END,
];

export const isRuleType = (type: unknown): type is RuleType =>
  Boolean(type) && RULE_TYPES.includes(type as string);

export const isRule = (rule: unknown): rule is Rule | RuleRef =>
  rule !== null &&
  rule !== undefined &&
  (rule instanceof RuleRef ||
    isRuleType((rule as { type?: unknown }).type));

export const isRuleRef = (rule: unknown): rule is RuleRef =>
  rule instanceof RuleRef;

const isTypedRule = (rule: unknown, type: RuleType): boolean =>
  rule !== null &&
  rule !== undefined &&
  !isRuleRef(rule) &&
  (rule as { type?: unknown }).type === type;

export const isRuleEnd = (rule: unknown): rule is RuleEnd =>
  isTypedRule(rule, RuleType.END);

export const isRuleChar = (rule: unknown): rule is RuleChar =>
  isTypedRule(rule, RuleType.CHAR);

export const isRuleCharExcluded = (rule: unknown): rule is RuleCharExclude =>
  isTypedRule(rule, RuleType.CHAR_EXCLUDE);

export const isRange = (range: unknown): range is Range =>
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
  pointer: GraphPointer
): boolean => isRuleCharExcluded(pointer.rule);
