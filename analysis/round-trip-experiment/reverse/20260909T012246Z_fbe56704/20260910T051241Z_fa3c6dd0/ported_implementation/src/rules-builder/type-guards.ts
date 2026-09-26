import { InternalRuleType } from './types.ts';
import type {
  InternalRuleDef,
  InternalRuleDefChar,
  InternalRuleDefNumericValue,
  InternalRuleDefWithoutValue,
} from './types.ts';

const INTERNAL_RULE_TYPES = new Set<unknown>(Object.values(InternalRuleType));

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  !!type && INTERNAL_RULE_TYPES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' && rule !== null && isRuleDefType((rule as InternalRuleDef).type);

const is = (rule: InternalRuleDef | undefined, type: InternalRuleType): boolean =>
  rule !== undefined && rule.type === type;

export const isRuleDefAlt = (
  rule?: InternalRuleDef
): rule is InternalRuleDefWithoutValue => is(rule, InternalRuleType.ALT);

export const isRuleDefRef = (
  rule?: InternalRuleDef
): rule is InternalRuleDefNumericValue => is(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (
  rule?: InternalRuleDef
): rule is InternalRuleDefWithoutValue => is(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  is(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  is(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef
): rule is InternalRuleDefNumericValue => is(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef
): rule is InternalRuleDefNumericValue => is(rule, InternalRuleType.CHAR_RNG_UPPER);
