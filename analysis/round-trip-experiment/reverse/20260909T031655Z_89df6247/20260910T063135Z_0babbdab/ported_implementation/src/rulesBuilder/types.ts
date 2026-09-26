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

export const INTERNAL_RULE_TYPES: InternalRuleType[] =
  Object.values(InternalRuleType);

export type InternalRuleDefValue = number | number[] | undefined;

/** A single linear rule definition, mirroring the reference's plain objects. */
export class InternalRuleDef {
  public type: InternalRuleType;
  public value: InternalRuleDefValue;

  public constructor(type: InternalRuleType, value?: InternalRuleDefValue) {
    this.type = type;
    this.value = value;
  }
}
