import {
  InternalRuleType,
  type InternalRuleDef,
  type InternalRuleDefAlt,
  type InternalRuleDefChar,
  type InternalRuleDefCharAlt,
  type InternalRuleDefCharNot,
  type InternalRuleDefCharRngUpper,
  type InternalRuleDefEnd,
  type InternalRuleDefRuleRef,
} from './types.js';

const INTERNAL_RULE_TYPES = new Set<string>(Object.values(InternalRuleType));

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  typeof type === 'string' && INTERNAL_RULE_TYPES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' &&
  rule !== null &&
  isRuleDefType((rule as InternalRuleDef).type);

export const isRuleDefAlt = (rule?: InternalRuleDef): rule is InternalRuleDefAlt =>
  rule?.type === InternalRuleType.ALT;

export const isRuleDefRef = (
  rule?: InternalRuleDef
): rule is InternalRuleDefRuleRef => rule?.type === InternalRuleType.RULE_REF;

export const isRuleDefEnd = (rule?: InternalRuleDef): rule is InternalRuleDefEnd =>
  rule?.type === InternalRuleType.END;

export const isRuleDefChar = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  rule?.type === InternalRuleType.CHAR;

export const isRuleDefCharNot = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharNot => rule?.type === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharAlt => rule?.type === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharRngUpper =>
  rule?.type === InternalRuleType.CHAR_RNG_UPPER;
