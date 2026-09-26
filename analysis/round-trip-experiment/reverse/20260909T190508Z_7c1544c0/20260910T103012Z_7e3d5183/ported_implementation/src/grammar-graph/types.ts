export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A range is a two element [start, end] list of code points.
export type Range = number[];
export type RuleValue = (number | Range)[];

export interface RuleChar {
  type: RuleType.CHAR;
  value: RuleValue;
}

export interface RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE;
  value: RuleValue;
}

export interface RuleEnd {
  type: RuleType.END;
}

export const ruleChar = (value: RuleValue = []): RuleChar => ({
  type: RuleType.CHAR,
  value,
});

export const ruleCharExclude = (value: RuleValue = []): RuleCharExclude => ({
  type: RuleType.CHAR_EXCLUDE,
  value,
});

export const ruleEnd = (): RuleEnd => ({ type: RuleType.END });

// UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number"
// (like "8") should be passed in as a string.
export type ValidInput = string | number | number[];

/**
 * The plain-data view of a rule, mirroring the reference implementation's JSON
 * shape (`{"type": "char", "value": [102]}`).
 */
export const ruleToDict = (
  rule: ResolvedRule
): { type: string; value?: RuleValue } => {
  if (rule.type === RuleType.END) {
    return { type: rule.type };
  }
  return { type: rule.type, value: rule.value };
};
