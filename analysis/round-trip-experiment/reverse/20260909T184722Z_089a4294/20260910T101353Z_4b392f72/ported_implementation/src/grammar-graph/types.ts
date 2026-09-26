export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A range is a two element list of code points, `[start, end]`.
export type Range = [number, number];

export type RuleCharValue = number | Range;

const copyValue = (value: readonly RuleCharValue[]): RuleCharValue[] =>
  value.map(v => (Array.isArray(v) ? ([...v] as Range) : v));

/** Char-matching rule, holding code points and/or ranges. */
export class RuleChar {
  type: RuleType.CHAR = RuleType.CHAR;
  value: RuleCharValue[];

  constructor(value: readonly RuleCharValue[]) {
    this.value = copyValue(value);
  }
}

/** Char-matching rule that matches anything _but_ its code points and/or ranges. */
export class RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE;
  value: RuleCharValue[];

  constructor(value: readonly RuleCharValue[]) {
    this.value = copyValue(value);
  }
}

export class RuleEnd {
  type: RuleType.END = RuleType.END;
}

export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];
