export enum InternalRuleType {
  CHAR = 'CHAR',
  CHAR_RNG_UPPER = 'CHAR_RNG_UPPER',
  RULE_REF = 'RULE_REF',
  ALT = 'ALT',
  END = 'END',

  CHAR_NOT = 'CHAR_NOT',
  CHAR_ALT = 'CHAR_ALT',
}

/** A rule as emitted by the RulesBuilder, before it is stacked into a graph. */
export type InternalRuleDefChar = {
  type: InternalRuleType.CHAR;
  value: number[];
};
export type InternalRuleDefCharNot = {
  type: InternalRuleType.CHAR_NOT;
  value: number[];
};
export type InternalRuleDefCharAlt = {
  type: InternalRuleType.CHAR_ALT;
  value: number;
};
export type InternalRuleDefCharRngUpper = {
  type: InternalRuleType.CHAR_RNG_UPPER;
  value: number;
};
export type InternalRuleDefRuleRef = {
  type: InternalRuleType.RULE_REF;
  value: number;
};
export type InternalRuleDefAlt = { type: InternalRuleType.ALT };
export type InternalRuleDefEnd = { type: InternalRuleType.END };

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefCharNot
  | InternalRuleDefCharAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefRuleRef
  | InternalRuleDefAlt
  | InternalRuleDefEnd;

export type InternalRuleDefWithNumericValue =
  | InternalRuleDefChar
  | InternalRuleDefCharNot;
