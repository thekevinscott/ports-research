import type { GraphPointer } from './graphPointer';
import { RuleRef } from './ruleRef';
import {
  ALL_RULE_TYPES,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from './types';
import type { Range, Rule, UnresolvedRule } from './types';

export const isRuleType = (type?: unknown): type is RuleType =>
  !!type && typeof type === 'string' && ALL_RULE_TYPES.has(type);

export const isRule = (rule?: unknown): rule is Rule =>
  !!rule &&
  typeof rule === 'object' &&
  'type' in rule &&
  isRuleType((rule as { type?: unknown }).type);

export const isRuleRef = (rule?: unknown): rule is RuleRef =>
  rule instanceof RuleRef;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd =>
  !!rule && !isRuleRef(rule) && rule.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar =>
  !!rule && !isRuleRef(rule) && rule.type === RuleType.CHAR;

export const isRuleCharExcluded = (
  rule?: UnresolvedRule,
): rule is RuleCharExclude =>
  !!rule && !isRuleRef(rule) && rule.type === RuleType.CHAR_EXCLUDE;

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
