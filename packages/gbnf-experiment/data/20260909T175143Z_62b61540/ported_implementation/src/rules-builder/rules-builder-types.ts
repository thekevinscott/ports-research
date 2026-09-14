export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_ALT = 'CHAR_ALT',
  CHAR_NOT = 'CHAR_NOT',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  ALT = 'ALT',
  END = 'END',
  RULE_REF = 'RULE_REF',
}

export interface InternalRuleDefChar {
  type: InternalRuleType.CHAR;
  value: number[];
}

export interface InternalRuleDefCharNot {
  type: InternalRuleType.CHAR_NOT;
  value: number[];
}

export interface InternalRuleDefCharAlt {
  type: InternalRuleType.CHAR_ALT;
  value: number;
}

export interface InternalRuleDefCharRngUpper {
  type: InternalRuleType.CHAR_RNG_UPPER;
  value: number;
}

export interface InternalRuleDefReference {
  type: InternalRuleType.RULE_REF;
  value: number;
}

export interface InternalRuleDefAlt {
  type: InternalRuleType.ALT;
}

export interface InternalRuleDefEnd {
  type: InternalRuleType.END;
}

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefCharNot
  | InternalRuleDefCharAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefReference
  | InternalRuleDefAlt
  | InternalRuleDefEnd;

export type InternalRuleDefCharOrAltChar = InternalRuleDefChar | InternalRuleDefCharAlt;

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

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharRngUpper => rule?.type === InternalRuleType.CHAR_RNG_UPPER;
