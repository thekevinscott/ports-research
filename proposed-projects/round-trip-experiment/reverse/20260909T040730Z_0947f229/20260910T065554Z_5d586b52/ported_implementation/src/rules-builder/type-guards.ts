/** Port of `gbnf/rules_builder/type_guards.py`. */

import { InternalRuleDef, InternalRuleType } from './types.js';

const INTERNAL_RULE_TYPES = new Set<string>(Object.values(InternalRuleType));

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  typeof type === 'string' && INTERNAL_RULE_TYPES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' &&
  rule !== null &&
  isRuleDefType((rule as { type?: unknown }).type);

const is = (rule: InternalRuleDef | undefined, type: InternalRuleType): boolean =>
  rule !== undefined && rule !== null && rule.type === type;

export const isRuleDefAlt = (rule?: InternalRuleDef): boolean =>
  is(rule, InternalRuleType.ALT);

export const isRuleDefRef = (rule?: InternalRuleDef): boolean =>
  is(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (rule?: InternalRuleDef): boolean =>
  is(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: InternalRuleDef): boolean =>
  is(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: InternalRuleDef): boolean =>
  is(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (rule?: InternalRuleDef): boolean =>
  is(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (rule?: InternalRuleDef): boolean =>
  is(rule, InternalRuleType.CHAR_RNG_UPPER);
