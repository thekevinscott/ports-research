import {
  InternalRuleDef,
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
  InternalRuleType,
} from './types';

const INTERNAL_RULE_TYPE_VALUES = new Set<unknown>(Object.values(InternalRuleType));

const typeOf = (rule: unknown): unknown =>
  rule !== null && typeof rule === 'object' ? (rule as { type?: unknown }).type : undefined;

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  Boolean(type) && INTERNAL_RULE_TYPE_VALUES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  Boolean(rule) && isRuleDefType(typeOf(rule));

export const isRuleDefAlt = (rule?: unknown): rule is InternalRuleDefAlt =>
  Boolean(rule) && typeOf(rule) === InternalRuleType.ALT;

export const isRuleDefRef = (rule?: unknown): rule is InternalRuleDefReference =>
  Boolean(rule) && typeOf(rule) === InternalRuleType.RULE_REF;

export const isRuleDefEnd = (rule?: unknown): rule is InternalRuleDefEnd =>
  Boolean(rule) && typeOf(rule) === InternalRuleType.END;

export const isRuleDefChar = (rule?: unknown): rule is InternalRuleDefChar =>
  Boolean(rule) && typeOf(rule) === InternalRuleType.CHAR;

export const isRuleDefCharNot = (rule?: unknown): rule is InternalRuleDefCharNot =>
  Boolean(rule) && typeOf(rule) === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (rule?: unknown): rule is InternalRuleDefCharAlt =>
  Boolean(rule) && typeOf(rule) === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (rule?: unknown): rule is InternalRuleDefCharRngUpper =>
  Boolean(rule) && typeOf(rule) === InternalRuleType.CHAR_RNG_UPPER;
