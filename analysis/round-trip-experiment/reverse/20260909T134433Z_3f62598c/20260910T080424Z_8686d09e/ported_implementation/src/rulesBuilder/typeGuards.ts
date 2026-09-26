import { InternalRuleType } from './types.js';
import type {
  InternalRuleDef,
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
} from './types.js';

const INTERNAL_RULE_TYPES = new Set<string>(Object.values(InternalRuleType));

export const isRuleDefType = (type?: unknown): type is InternalRuleType =>
  typeof type === 'string' && INTERNAL_RULE_TYPES.has(type);

export const isRuleDef = (rule?: unknown): rule is InternalRuleDef =>
  typeof rule === 'object' && rule !== null && isRuleDefType((rule as { type?: unknown; }).type);

const isRuleDefOfType = (rule: unknown, type: InternalRuleType): boolean =>
  typeof rule === 'object' && rule !== null && (rule as { type?: unknown; }).type === type;

export const isRuleDefAlt = (rule?: unknown): rule is InternalRuleDefAlt =>
  isRuleDefOfType(rule, InternalRuleType.ALT);

export const isRuleDefRef = (rule?: unknown): rule is InternalRuleDefReference =>
  isRuleDefOfType(rule, InternalRuleType.RULE_REF);

export const isRuleDefEnd = (rule?: unknown): rule is InternalRuleDefEnd =>
  isRuleDefOfType(rule, InternalRuleType.END);

export const isRuleDefChar = (rule?: unknown): rule is InternalRuleDefChar =>
  isRuleDefOfType(rule, InternalRuleType.CHAR);

export const isRuleDefCharNot = (rule?: unknown): rule is InternalRuleDefCharNot =>
  isRuleDefOfType(rule, InternalRuleType.CHAR_NOT);

export const isRuleDefCharAlt = (rule?: unknown): rule is InternalRuleDefCharAlt =>
  isRuleDefOfType(rule, InternalRuleType.CHAR_ALT);

export const isRuleDefCharRngUpper = (rule?: unknown): rule is InternalRuleDefCharRngUpper =>
  isRuleDefOfType(rule, InternalRuleType.CHAR_RNG_UPPER);
