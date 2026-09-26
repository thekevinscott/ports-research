import type { GraphPointer } from './graph-pointer.js';
import { RuleRef } from './rule-ref.js';
import {
  AbstractRule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
  type Range,
  type Rule,
} from './types.js';

export type UnresolvedRule = Rule | RuleRef;

export const isRuleType = (type?: unknown): type is RuleType =>
  typeof type === 'string' && Object.values(RuleType).includes(type as RuleType);

export const isRule = (rule?: unknown): rule is UnresolvedRule =>
  rule instanceof AbstractRule || rule instanceof RuleRef;

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd => rule instanceof RuleEnd;

export const isRuleChar = (rule?: unknown): rule is RuleChar => rule instanceof RuleChar;

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  rule instanceof RuleCharExclude;

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) && range.length === 2 && range.every(n => typeof n === 'number');

export const isGraphPointerRuleRef = (pointer: GraphPointer): boolean => isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): boolean => isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: GraphPointer): boolean => isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: GraphPointer): boolean =>
  isRuleCharExcluded(pointer.rule);
