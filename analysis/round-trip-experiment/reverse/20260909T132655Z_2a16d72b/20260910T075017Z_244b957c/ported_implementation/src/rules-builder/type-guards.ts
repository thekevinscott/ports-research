import { InternalRuleDef, InternalRuleType } from './types.js';

const INTERNAL_RULE_TYPES: string[] = [
  InternalRuleType.CHAR,
  InternalRuleType.CHAR_RNG_UPPER,
  InternalRuleType.RULE_REF,
  InternalRuleType.ALT,
  InternalRuleType.END,
  InternalRuleType.CHAR_NOT,
  InternalRuleType.CHAR_ALT,
];

export const isRuleDefType = (type: unknown): type is InternalRuleType =>
  Boolean(type) && INTERNAL_RULE_TYPES.includes(type as string);

export const isRuleDef = (rule: unknown): rule is InternalRuleDef =>
  rule !== null &&
  rule !== undefined &&
  isRuleDefType((rule as { type?: unknown }).type);

const is = (
  rule: InternalRuleDef | undefined | null,
  type: InternalRuleType
): boolean => rule !== null && rule !== undefined && rule.type === type;

export const isRuleDefAlt = (rule?: InternalRuleDef | null): boolean =>
  is(rule, InternalRuleType.ALT);

export const isRuleDefRef = (rule?: InternalRuleDef | null): boolean =>
  is(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (rule?: InternalRuleDef | null): boolean =>
  is(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: InternalRuleDef | null): boolean =>
  is(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: InternalRuleDef | null): boolean =>
  is(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (rule?: InternalRuleDef | null): boolean =>
  is(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (rule?: InternalRuleDef | null): boolean =>
  is(rule, InternalRuleType.CHAR_RNG_UPPER);
