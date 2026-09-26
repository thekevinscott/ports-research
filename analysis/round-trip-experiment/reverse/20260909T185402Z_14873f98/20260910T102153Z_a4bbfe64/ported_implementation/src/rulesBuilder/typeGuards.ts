import { ALL_INTERNAL_RULE_TYPES, InternalRuleType } from './types';
import type {
  InternalRuleDef,
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefRuleRef,
} from './types';

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  !!type && typeof type === 'string' && ALL_INTERNAL_RULE_TYPES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  !!rule &&
  typeof rule === 'object' &&
  'type' in rule &&
  isRuleDefType((rule as { type?: unknown }).type);

export const isRuleDefAlt = (rule?: InternalRuleDef): rule is InternalRuleDefAlt =>
  !!rule && rule.type === InternalRuleType.ALT;

export const isRuleDefRef = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefRuleRef =>
  !!rule && rule.type === InternalRuleType.RULE_REF;

export const isRuleDefEnd = (rule?: InternalRuleDef): rule is InternalRuleDefEnd =>
  !!rule && rule.type === InternalRuleType.END;

export const isRuleDefChar = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefChar => !!rule && rule.type === InternalRuleType.CHAR;

export const isRuleDefCharNot = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharNot =>
  !!rule && rule.type === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharAlt =>
  !!rule && rule.type === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharRngUpper =>
  !!rule && rule.type === InternalRuleType.CHAR_RNG_UPPER;
