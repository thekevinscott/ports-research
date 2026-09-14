export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
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

/** A single entry of a linearized rule. */
export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefCharNot
  | InternalRuleDefCharAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefReference
  | InternalRuleDefAlt
  | InternalRuleDefEnd;
