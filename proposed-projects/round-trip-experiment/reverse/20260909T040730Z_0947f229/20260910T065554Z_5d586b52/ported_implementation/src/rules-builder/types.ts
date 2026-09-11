/** Port of `gbnf/rules_builder/types.py`. */

export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

export type InternalRuleValue = number | number[] | undefined;

export interface InternalRuleDef {
  type: InternalRuleType;
  value?: InternalRuleValue;
}

export const internalRuleDef = (
  type: InternalRuleType,
  value?: InternalRuleValue,
): InternalRuleDef => (value === undefined ? { type } : { type, value });

// Indexed by rule id; `undefined` marks a symbol that was referenced but never
// defined (a hole in the sparse array).
export type InternalRuleDefs = (InternalRuleDef[] | undefined)[];
