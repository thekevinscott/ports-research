import type { GraphPointer } from './graph-pointer.js';
import { RuleRef } from './rule-ref.js';
import {
  Range,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
  UnresolvedRule,
} from './types.js';

export const isRuleType = (type?: unknown): type is RuleType =>
  !!type && Object.values(RuleType).includes(type as RuleType);

export const isRule = (rule?: unknown): rule is UnresolvedRule =>
  rule instanceof RuleRef ||
  (typeof rule === 'object' && rule !== null && isRuleType((rule as { type: unknown }).type));

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

const isType = <R extends UnresolvedRule>(rule: unknown, type: RuleType): rule is R =>
  typeof rule === 'object' &&
  rule !== null &&
  (rule as { type?: unknown }).type === type;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd =>
  isType<RuleEnd>(rule, RuleType.END);

export const isRuleChar = (rule?: unknown): rule is RuleChar =>
  isType<RuleChar>(rule, RuleType.CHAR);

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  isType<RuleCharExclude>(rule, RuleType.CHAR_EXCLUDE);

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
