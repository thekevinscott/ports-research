export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

export interface InternalRuleDef {
  type: InternalRuleType;
  value?: number | number[];
}

export const ruleDef = (type: InternalRuleType, value?: number | number[]): InternalRuleDef =>
  value === undefined ? { type } : { type, value };

export type InternalRuleDefs = InternalRuleDef[];
