export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

/** A plain record of a rule type and, for most types, a value. */
export class InternalRuleDef {
  public type: InternalRuleType;
  public value?: number | number[];

  constructor(type: InternalRuleType, value?: number | number[]) {
    this.type = type;
    this.value = value;
  }

  toString(): string {
    if (this.value === undefined) {
      return `{type: ${this.type}}`;
    }
    return `{type: ${this.type}, value: ${JSON.stringify(this.value)}}`;
  }
}
