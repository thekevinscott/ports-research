import { InternalRuleType } from './types';
import type { InternalRuleDef } from './types';

export const isRuleDefType = (type: unknown): type is InternalRuleType =>
  Boolean(type) && Object.values(InternalRuleType).includes(type as InternalRuleType);

export const isRuleDef = (rule: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' &&
  rule !== null &&
  'type' in rule &&
  isRuleDefType((rule as InternalRuleDef).type);

const isType = (rule: InternalRuleDef | undefined, type: InternalRuleType): boolean =>
  rule !== undefined && rule.type === type;

export const isRuleDefAlt = (rule?: InternalRuleDef): boolean =>
  isType(rule, InternalRuleType.ALT);

export const isRuleDefRef = (rule?: InternalRuleDef): boolean =>
  isType(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (rule?: InternalRuleDef): boolean =>
  isType(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: InternalRuleDef): boolean =>
  isType(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: InternalRuleDef): boolean =>
  isType(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (rule?: InternalRuleDef): boolean =>
  isType(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (rule?: InternalRuleDef): boolean =>
  isType(rule, InternalRuleType.CHAR_RNG_UPPER);
