import { InternalRuleDef, InternalRuleType } from './types.js';

const INTERNAL_RULE_TYPE_VALUES = new Set<string>(
  Object.values(InternalRuleType),
);

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  !!type && typeof type === 'string' && INTERNAL_RULE_TYPE_VALUES.has(type);

export const isRuleDef = (rule?: InternalRuleDef): rule is InternalRuleDef =>
  rule !== undefined && rule !== null && isRuleDefType(rule.type);

export const isRuleDefAlt = (rule?: InternalRuleDef): boolean =>
  !!rule && rule.type === InternalRuleType.ALT;

export const isRuleDefRef = (rule?: InternalRuleDef): boolean =>
  !!rule && rule.type === InternalRuleType.RULE_REF;

export const isRuleDefEnd = (rule?: InternalRuleDef): boolean =>
  !!rule && rule.type === InternalRuleType.END;

export const isRuleDefChar = (rule?: InternalRuleDef): boolean =>
  !!rule && rule.type === InternalRuleType.CHAR;

export const isRuleDefCharNot = (rule?: InternalRuleDef): boolean =>
  !!rule && rule.type === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (rule?: InternalRuleDef): boolean =>
  !!rule && rule.type === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (rule?: InternalRuleDef): boolean =>
  !!rule && rule.type === InternalRuleType.CHAR_RNG_UPPER;
