import {
  INTERNAL_RULE_TYPES,
  InternalRuleDef,
  InternalRuleType,
} from './types.js';

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  Boolean(type) && INTERNAL_RULE_TYPES.includes(type as InternalRuleType);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  rule instanceof InternalRuleDef && isRuleDefType(rule.type);

const is = (rule: InternalRuleDef | undefined | null, type: InternalRuleType) =>
  rule !== undefined && rule !== null && rule.type === type;

export const isRuleDefAlt = (rule?: InternalRuleDef | null) =>
  is(rule, InternalRuleType.ALT);

export const isRuleDefRef = (rule?: InternalRuleDef | null) =>
  is(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (rule?: InternalRuleDef | null) =>
  is(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: InternalRuleDef | null) =>
  is(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: InternalRuleDef | null) =>
  is(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (rule?: InternalRuleDef | null) =>
  is(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (rule?: InternalRuleDef | null) =>
  is(rule, InternalRuleType.CHAR_RNG_UPPER);
