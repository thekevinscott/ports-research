import { RuleRef } from './rule-ref.js';
import {
  type Range,
  type ResolvedRule,
  type RuleChar,
  type RuleCharExclude,
  type RuleEnd,
  RuleType,
} from './types.js';

/** Any rule the graph can hold, including the internal reference rules. */
export type UnresolvedRule = ResolvedRule | RuleRef;

const RULE_TYPES = new Set<string>(Object.values(RuleType));

export const isRuleType = (type?: unknown): type is RuleType =>
  typeof type === 'string' && type !== '' && RULE_TYPES.has(type);

export const isRule = (rule?: unknown): rule is UnresolvedRule => {
  if (rule instanceof RuleRef) {
    return true;
  }
  return (
    typeof rule === 'object' &&
    rule !== null &&
    isRuleType((rule as { type?: unknown }).type)
  );
};

export const isRuleRef = (rule?: unknown): rule is RuleRef => rule instanceof RuleRef;

export const isRuleEnd = (rule?: UnresolvedRule): rule is RuleEnd =>
  rule !== undefined && !isRuleRef(rule) && rule.type === RuleType.END;

export const isRuleChar = (rule?: UnresolvedRule): rule is RuleChar =>
  rule !== undefined && !isRuleRef(rule) && rule.type === RuleType.CHAR;

export const isRuleCharExcluded = (rule?: UnresolvedRule): rule is RuleCharExclude =>
  rule !== undefined && !isRuleRef(rule) && rule.type === RuleType.CHAR_EXCLUDE;

export const isRange = (range?: unknown): range is Range =>
  Array.isArray(range) &&
  range.length === 2 &&
  range.every((n) => typeof n === 'number');

interface HasRule {
  rule: UnresolvedRule;
}

export const isGraphPointerRuleRef = <T extends HasRule>(
  pointer: T
): pointer is T & { rule: RuleRef } => isRuleRef(pointer.rule);

export const isGraphPointerRuleEnd = <T extends HasRule>(
  pointer: T
): pointer is T & { rule: RuleEnd } => isRuleEnd(pointer.rule);

export const isGraphPointerRuleChar = <T extends HasRule>(
  pointer: T
): pointer is T & { rule: RuleChar } => isRuleChar(pointer.rule);

export const isGraphPointerRuleCharExclude = <T extends HasRule>(
  pointer: T
): pointer is T & { rule: RuleCharExclude } => isRuleCharExcluded(pointer.rule);
