import {
  type InternalRuleDef,
  type InternalRuleDefAlt,
  type InternalRuleDefChar,
  type InternalRuleDefCharAlt,
  type InternalRuleDefCharNot,
  type InternalRuleDefCharRngUpper,
  type InternalRuleDefEnd,
  type InternalRuleDefRuleRef,
  InternalRuleType,
} from './types.ts';

const INTERNAL_RULE_TYPES: string[] = Object.values(InternalRuleType);

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  !!type && typeof type === 'string' && INTERNAL_RULE_TYPES.includes(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  !!rule &&
  typeof rule === 'object' &&
  isRuleDefType((rule as { type?: unknown }).type);

/** `rule.type` is `undefined` for anything that isn't a rule def. */
const ruleType = (rule: unknown): unknown =>
  rule && typeof rule === 'object' ? (rule as { type?: unknown }).type : undefined;

export const isRuleDefAlt = (rule?: InternalRuleDef): rule is InternalRuleDefAlt =>
  !!rule && ruleType(rule) === InternalRuleType.ALT;

export const isRuleDefRef = (rule?: InternalRuleDef): rule is InternalRuleDefRuleRef =>
  !!rule && ruleType(rule) === InternalRuleType.RULE_REF;

export const isRuleDefEnd = (rule?: InternalRuleDef): rule is InternalRuleDefEnd =>
  !!rule && ruleType(rule) === InternalRuleType.END;

export const isRuleDefChar = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  !!rule && ruleType(rule) === InternalRuleType.CHAR;

export const isRuleDefCharNot = (rule?: InternalRuleDef): rule is InternalRuleDefCharNot =>
  !!rule && ruleType(rule) === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (rule?: InternalRuleDef): rule is InternalRuleDefCharAlt =>
  !!rule && ruleType(rule) === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharRngUpper =>
  !!rule && ruleType(rule) === InternalRuleType.CHAR_RNG_UPPER;
