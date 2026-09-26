export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

// Internal rule definitions carry a code point, a list of code points, or, for ALT and
// END, no value at all.
export interface InternalRuleDef {
  type: InternalRuleType;
  value?: number | number[];
}
