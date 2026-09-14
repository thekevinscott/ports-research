import type { GraphPointer } from './graph-pointer';
import { RuleRef } from './rule-ref';
import {
  Range,
  Rule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from './types';

const RULE_TYPE_VALUES = new Set<unknown>(Object.values(RuleType));

const typeOf = (rule: unknown): unknown =>
  rule !== null && typeof rule === 'object' ? (rule as { type?: unknown }).type : undefined;

export const isRuleType = (type?: unknown): type is RuleType =>
  Boolean(type) && RULE_TYPE_VALUES.has(type);

export const isRule = (rule?: unknown): rule is Rule =>
  Boolean(rule) && isRuleType(typeOf(rule));

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd =>
  Boolean(rule) && !isRuleRef(rule) && typeOf(rule) === RuleType.END;

export const isRuleChar = (rule?: unknown): rule is RuleChar =>
  Boolean(rule) && !isRuleRef(rule) && typeOf(rule) === RuleType.CHAR;

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  Boolean(rule) && !isRuleRef(rule) && typeOf(rule) === RuleType.CHAR_EXCLUDE;

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) && range.length === 2 && range.every((n) => typeof n === 'number');

export const isGraphPointerRuleRef = (pointer: GraphPointer): boolean =>
  isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): boolean =>
  isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: GraphPointer): boolean =>
  isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: GraphPointer): boolean =>
  isRuleCharExcluded(pointer.rule);
