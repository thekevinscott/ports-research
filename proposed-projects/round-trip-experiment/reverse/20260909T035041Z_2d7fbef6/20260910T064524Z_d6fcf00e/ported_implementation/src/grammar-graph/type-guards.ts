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

export const isRuleType = (type?: unknown): type is RuleType =>
  !!type && Object.values(RuleType).includes(type as RuleType);

export const isRule = (rule?: unknown): rule is Rule =>
  typeof rule === 'object' && rule !== null && isRuleType((rule as Rule).type);

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd =>
  isRule(rule) && rule.type === RuleType.END;

export const isRuleChar = (rule?: unknown): rule is RuleChar =>
  isRule(rule) && rule.type === RuleType.CHAR;

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  isRule(rule) && rule.type === RuleType.CHAR_EXCLUDE;

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
