export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  // CHAR_RNG = 'CHAR_RNG',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

export class InternalRuleDef {
  public type: InternalRuleType;
  public value?: number | number[];

  constructor(type: InternalRuleType, value?: number | number[]) {
    this.type = type;
    this.value = value;
  }
}
