export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

/**
 * A single element of a linear (pre-stacked) rule definition.
 *
 * CHAR and CHAR_NOT carry a list of code points; RULE_REF, CHAR_ALT and
 * CHAR_RNG_UPPER carry a single number; ALT and END carry no value.
 */
export interface InternalRuleDefChar {
  type: InternalRuleType.CHAR | InternalRuleType.CHAR_NOT;
  value: number[];
}

export interface InternalRuleDefNumericValue {
  type:
    | InternalRuleType.RULE_REF
    | InternalRuleType.CHAR_ALT
    | InternalRuleType.CHAR_RNG_UPPER;
  value: number;
}

export interface InternalRuleDefWithoutValue {
  type: InternalRuleType.ALT | InternalRuleType.END;
}

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefNumericValue
  | InternalRuleDefWithoutValue;
