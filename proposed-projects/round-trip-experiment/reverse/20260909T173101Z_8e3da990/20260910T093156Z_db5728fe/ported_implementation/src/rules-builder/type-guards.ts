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
} from './types.js';

export const isRuleDefType = (type?: unknown): type is InternalRuleType => {
  if (!type) {
    return false;
  }
  return Object.values(InternalRuleType).includes(type as InternalRuleType);
};

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  !!rule && isRuleDefType((rule as { type?: unknown; }).type);

export const isRuleDefAlt = (rule?: InternalRuleDef): rule is InternalRuleDefAlt =>
  rule?.type === InternalRuleType.ALT;

export const isRuleDefRef = (rule?: InternalRuleDef): rule is InternalRuleDefReference =>
  rule?.type === InternalRuleType.RULE_REF;

export const isRuleDefEnd = (rule?: InternalRuleDef): rule is InternalRuleDefEnd =>
  rule?.type === InternalRuleType.END;

export const isRuleDefChar = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  rule?.type === InternalRuleType.CHAR;

export const isRuleDefCharNot = (rule?: InternalRuleDef): rule is InternalRuleDefCharNot =>
  rule?.type === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (rule?: InternalRuleDef): rule is InternalRuleDefCharAlt =>
  rule?.type === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (rule?: InternalRuleDef): rule is InternalRuleDefCharRngUpper =>
  rule?.type === InternalRuleType.CHAR_RNG_UPPER;
