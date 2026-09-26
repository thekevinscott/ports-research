export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

// CHAR/CHAR_NOT carry an array of code points, the rest a bare number.
export interface InternalRuleDefChar {
  type: InternalRuleType.CHAR | InternalRuleType.CHAR_NOT;
  value: number[];
}

export interface InternalRuleDefWithNumericValue {
  type:
  | InternalRuleType.CHAR_RNG_UPPER
  | InternalRuleType.RULE_REF
  | InternalRuleType.CHAR_ALT;
  value: number;
}

export interface InternalRuleDefWithoutValue {
  type: InternalRuleType.ALT | InternalRuleType.END;
  value?: undefined;
}

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefWithNumericValue
  | InternalRuleDefWithoutValue;
