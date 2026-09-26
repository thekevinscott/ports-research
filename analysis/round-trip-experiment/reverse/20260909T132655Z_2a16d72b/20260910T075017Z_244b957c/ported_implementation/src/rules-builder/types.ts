export const InternalRuleType = {
  CHAR: 'CHAR',
  CHAR_RNG_UPPER: 'CHAR_RNG_UPPER',
  RULE_REF: 'RULE_REF',
  ALT: 'ALT',
  END: 'END',

  CHAR_NOT: 'CHAR_NOT',
  CHAR_ALT: 'CHAR_ALT',
} as const;

export type InternalRuleType =
  (typeof InternalRuleType)[keyof typeof InternalRuleType];

/**
 * A single entry in the linear rule definition list.
 *
 * `value` is an array of code points for CHAR/CHAR_NOT, a single number for
 * CHAR_ALT/CHAR_RNG_UPPER/RULE_REF, and absent for ALT/END.
 */
export class InternalRuleDef {
  type: InternalRuleType;
  value?: number | number[];

  constructor(type: InternalRuleType, value?: number | number[]) {
    this.type = type;
    this.value = value;
  }

  toString(): string {
    if (this.value === undefined) {
      return `InternalRuleDef(${this.type})`;
    }
    return `InternalRuleDef(${this.type}, ${JSON.stringify(this.value)})`;
  }
}
