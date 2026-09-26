import type { GraphPointer } from './graph-pointer.ts';
import { RuleRef } from './rule-ref.ts';
import {
  type Range,
  type RuleChar,
  type RuleCharExclude,
  type RuleEnd,
  RuleType,
  type UnresolvedRule,
} from './types.ts';

const RULE_TYPES: string[] = Object.values(RuleType);

export const isRuleType = (type?: unknown): type is RuleType =>
  !!type && typeof type === 'string' && RULE_TYPES.includes(type);

export const isRule = (rule?: unknown): rule is UnresolvedRule =>
  isRuleRef(rule) ||
  (!!rule && typeof rule === 'object' && isRuleType((rule as { type?: unknown }).type));

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

/** `rule.type` is `undefined` for anything that isn't a rule, never an error. */
const ruleType = (rule: unknown): unknown =>
  rule && typeof rule === 'object' ? (rule as { type?: unknown }).type : undefined;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd =>
  !!rule && !isRuleRef(rule) && ruleType(rule) === RuleType.END;

export const isRuleChar = (rule?: unknown): rule is RuleChar =>
  !!rule && !isRuleRef(rule) && ruleType(rule) === RuleType.CHAR;

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  !!rule && !isRuleRef(rule) && ruleType(rule) === RuleType.CHAR_EXCLUDE;

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
