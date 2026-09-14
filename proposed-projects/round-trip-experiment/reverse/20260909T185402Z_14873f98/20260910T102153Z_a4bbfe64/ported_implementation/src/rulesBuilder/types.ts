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

export const ALL_INTERNAL_RULE_TYPES: ReadonlySet<string> = new Set<string>(
  Object.values(InternalRuleType),
);

export interface InternalRuleDefChar {
  type: typeof InternalRuleType.CHAR;
  value: number[];
}
export interface InternalRuleDefCharNot {
  type: typeof InternalRuleType.CHAR_NOT;
  value: number[];
}
export interface InternalRuleDefCharAlt {
  type: typeof InternalRuleType.CHAR_ALT;
  value: number;
}
export interface InternalRuleDefCharRngUpper {
  type: typeof InternalRuleType.CHAR_RNG_UPPER;
  value: number;
}
export interface InternalRuleDefRuleRef {
  type: typeof InternalRuleType.RULE_REF;
  value: number;
}
export interface InternalRuleDefAlt {
  type: typeof InternalRuleType.ALT;
}
export interface InternalRuleDefEnd {
  type: typeof InternalRuleType.END;
}

/**
 * A rule definition emitted by the rules builder.
 *
 * `value` is a list of code points for CHAR/CHAR_NOT, a single number for
 * RULE_REF/CHAR_ALT/CHAR_RNG_UPPER, and absent for ALT/END.
 */
export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefCharNot
  | InternalRuleDefCharAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefRuleRef
  | InternalRuleDefAlt
  | InternalRuleDefEnd;
