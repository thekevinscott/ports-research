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
 * A rule definition emitted by the RulesBuilder.
 *
 * `value` is a list of code points for CHAR/CHAR_NOT, a single code point for
 * CHAR_ALT/CHAR_RNG_UPPER, a rule id for RULE_REF, and absent for ALT/END.
 */
export class InternalRuleDef {
  public type: InternalRuleType;
  public value?: number | number[];

  constructor(type: InternalRuleType, value?: number | number[]) {
    this.type = type;
    this.value = value;
  }
}
