import {
  type InternalRuleDef,
  type InternalRuleDefAlt,
  type InternalRuleDefChar,
  type InternalRuleDefCharAlt,
  type InternalRuleDefCharNot,
  type InternalRuleDefCharRngUpper,
  type InternalRuleDefEnd,
  type InternalRuleDefReference,
  InternalRuleType,
} from './types.js';

const RULE_DEF_TYPES = new Set<string>(Object.values(InternalRuleType));

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  typeof type === 'string' && type !== '' && RULE_DEF_TYPES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' &&
  rule !== null &&
  isRuleDefType((rule as { type?: unknown }).type);

const is = (rule: InternalRuleDef | undefined, type: InternalRuleType): boolean =>
  rule !== undefined && rule.type === type;

export const isRuleDefAlt = (rule?: InternalRuleDef): rule is InternalRuleDefAlt =>
  is(rule, InternalRuleType.ALT);

export const isRuleDefRef = (rule?: InternalRuleDef): rule is InternalRuleDefReference =>
  is(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (rule?: InternalRuleDef): rule is InternalRuleDefEnd =>
  is(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  is(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: InternalRuleDef): rule is InternalRuleDefCharNot =>
  is(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (rule?: InternalRuleDef): rule is InternalRuleDefCharAlt =>
  is(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharRngUpper => is(rule, InternalRuleType.CHAR_RNG_UPPER);
