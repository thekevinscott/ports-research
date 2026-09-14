export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

/** A range is a two element `[start, end]` pair of code points. */
export type Range = [number, number];

/** A single code point, or a range of them. */
export type RuleCharValue = number | Range;

export interface RuleChar {
  type: RuleType.CHAR;
  value: RuleCharValue[];
}

export interface RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE;
  value: RuleCharValue[];
}

export interface RuleEnd {
  type: RuleType.END;
}

/** RuleRefs should never be exposed to the end user. */
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

/**
 * ValidInput can either be a string, or a number indicating a code point.
 * It CANNOT be a number representing a number; a number being a "number" (like "8")
 * should be passed in as a string.
 */
export type ValidInput = string | number | number[];
