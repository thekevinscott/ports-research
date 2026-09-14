import { InternalRuleDef, InternalRuleType } from './types.js';

const RULE_DEF_TYPES = new Set<string>(Object.values(InternalRuleType));

export const isRuleDefType = (type?: unknown): boolean =>
  Boolean(type) && typeof type === 'string' && RULE_DEF_TYPES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' &&
  rule !== null &&
  isRuleDefType((rule as InternalRuleDef).type);

const is = (
  rule: InternalRuleDef | undefined | null,
  type: InternalRuleType
): boolean => rule !== undefined && rule !== null && rule.type === type;

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
