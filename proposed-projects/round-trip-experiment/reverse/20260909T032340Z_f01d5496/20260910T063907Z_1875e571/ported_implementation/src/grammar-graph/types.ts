export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A Range is a two element array of code points, [start, end], inclusive.
export type Range = [number, number];

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export type RuleCharValue = number | Range;

/** Base for the rules that carry a list of code points and/or ranges. */
class RuleWithValue {
  public value: RuleCharValue[];

  constructor(value: Iterable<RuleCharValue>) {
    this.value = [...value].map((v) => (Array.isArray(v) ? ([...v] as Range) : v));
  }
}

export class RuleChar extends RuleWithValue {
  public type = RuleType.CHAR;
}

export class RuleCharExclude extends RuleWithValue {
  public type = RuleType.CHAR_EXCLUDE;
}

export class RuleEnd {
  public type = RuleType.END;
}

export type Rule = RuleChar | RuleCharExclude | RuleEnd;
