/** Port of `gbnf/grammar_graph/type_guards.py`. */

import { RuleRef } from './rule-ref.js';
import {
  Range,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
  UnresolvedRule,
} from './types.js';
import type { GraphPointer } from './graph-pointer.js';

const RULE_TYPES = new Set<string>(Object.values(RuleType));

export const isRuleType = (type?: unknown): type is RuleType =>
  typeof type === 'string' && RULE_TYPES.has(type);

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRule = (rule?: unknown): rule is UnresolvedRule =>
  isRuleRef(rule) ||
  (typeof rule === 'object' && rule !== null && isRuleType((rule as { type?: unknown }).type));

const isType = (rule: unknown, type: RuleType): boolean =>
  !isRuleRef(rule) &&
  typeof rule === 'object' &&
  rule !== null &&
  (rule as { type?: unknown }).type === type;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd => isType(rule, RuleType.END);

export const isRuleChar = (rule?: unknown): rule is RuleChar => isType(rule, RuleType.CHAR);

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  isType(rule, RuleType.CHAR_EXCLUDE);

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) &&
  range.length === 2 &&
  range.every((n) => typeof n === 'number' && Number.isFinite(n));

export const isGraphPointerRuleRef = (pointer: GraphPointer): boolean =>
  isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): boolean =>
  isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: GraphPointer): boolean =>
  isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: GraphPointer): boolean =>
  isRuleCharExcluded(pointer.rule);
