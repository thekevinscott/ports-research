import {
  InternalRuleDef,
  InternalRuleDefChar,
  InternalRuleDefWithNumericValue,
  InternalRuleDefWithoutValue,
  InternalRuleType,
} from './types.js';

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  !!type && Object.values(InternalRuleType).includes(type as InternalRuleType);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' && rule !== null && isRuleDefType((rule as InternalRuleDef).type);

const is = <R extends InternalRuleDef>(rule: unknown, type: InternalRuleType): rule is R =>
  isRuleDef(rule) && rule.type === type;

export const isRuleDefAlt = (rule?: unknown): rule is InternalRuleDefWithoutValue =>
  is(rule, InternalRuleType.ALT);

export const isRuleDefRef = (rule?: unknown): rule is InternalRuleDefWithNumericValue =>
  is(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (rule?: unknown): rule is InternalRuleDefWithoutValue =>
  is(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: unknown): rule is InternalRuleDefChar =>
  is(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: unknown): rule is InternalRuleDefChar =>
  is(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (rule?: unknown): rule is InternalRuleDefWithNumericValue =>
  is(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (
  rule?: unknown,
): rule is InternalRuleDefWithNumericValue => is(rule, InternalRuleType.CHAR_RNG_UPPER);
