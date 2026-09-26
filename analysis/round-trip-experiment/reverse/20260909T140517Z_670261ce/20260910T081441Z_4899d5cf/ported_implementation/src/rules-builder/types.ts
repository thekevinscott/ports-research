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
 * A single element of a linear rule definition.
 *
 * `value` is a list of code points for `CHAR` and `CHAR_NOT`, a single number for
 * `RULE_REF`/`CHAR_ALT`/`CHAR_RNG_UPPER`, and absent for `ALT`/`END`.
 */
export interface InternalRuleDef {
  type: InternalRuleType;
  value?: number | number[];
}

export interface InternalRuleDefChar extends InternalRuleDef {
  type: InternalRuleType.CHAR;
  value: number[];
}

export interface InternalRuleDefCharNot extends InternalRuleDef {
  type: InternalRuleType.CHAR_NOT;
  value: number[];
}

export interface InternalRuleDefCharAlt extends InternalRuleDef {
  type: InternalRuleType.CHAR_ALT;
  value: number;
}

export interface InternalRuleDefCharRngUpper extends InternalRuleDef {
  type: InternalRuleType.CHAR_RNG_UPPER;
  value: number;
}

export interface InternalRuleDefReference extends InternalRuleDef {
  type: InternalRuleType.RULE_REF;
  value: number;
}

export interface InternalRuleDefEnd extends InternalRuleDef {
  type: InternalRuleType.END;
}

export interface InternalRuleDefAlt extends InternalRuleDef {
  type: InternalRuleType.ALT;
}
