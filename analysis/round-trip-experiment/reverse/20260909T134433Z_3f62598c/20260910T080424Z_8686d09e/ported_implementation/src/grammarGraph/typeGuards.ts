import type { GraphPointer } from './graphPointer.js';
import { RuleRef } from './ruleRef.js';
import { RuleType } from './types.js';
import type { Range, RuleChar, RuleCharExclude, RuleEnd, UnresolvedRule } from './types.js';

const RULE_TYPES = new Set<string>(Object.values(RuleType));

export const isRuleType = (type?: unknown): type is RuleType =>
  typeof type === 'string' && RULE_TYPES.has(type);

export const isRule = (rule?: unknown): rule is UnresolvedRule => {
  if (rule === undefined || rule === null) {
    return false;
  }
  return rule instanceof RuleRef || isRuleType((rule as { type?: unknown; }).type);
};

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

const isRuleOfType = (rule: unknown, type: RuleType): boolean =>
  typeof rule === 'object' && rule !== null && (rule as { type?: unknown; }).type === type;

export const isRuleEnd = (rule?: unknown): rule is RuleEnd => isRuleOfType(rule, RuleType.END);

export const isRuleChar = (rule?: unknown): rule is RuleChar => isRuleOfType(rule, RuleType.CHAR);

export const isRuleCharExcluded = (rule?: unknown): rule is RuleCharExclude =>
  isRuleOfType(rule, RuleType.CHAR_EXCLUDE);

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) && range.length === 2 && range.every(n => typeof n === 'number');

export const isGraphPointerRuleRef = (pointer: GraphPointer): boolean => isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = (pointer: GraphPointer): boolean => isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = (pointer: GraphPointer): boolean => isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = (pointer: GraphPointer): boolean =>
  isRuleCharExcluded(pointer.rule);
