/** Rule types exposed by the parser, and the union types built on top of them. */

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A range is a two element list of code points, inclusive on both ends.
export type Range = [number, number];

export type RuleCharValue = number | Range;

export class RuleChar {
  public type: RuleType.CHAR = RuleType.CHAR;
  public value: RuleCharValue[];

  constructor(value: RuleCharValue[]) {
    this.value = [...value];
  }
}

export class RuleCharExclude {
  public type: RuleType.CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE;
  public value: RuleCharValue[];

  constructor(value: RuleCharValue[]) {
    this.value = [...value];
  }
}

export class RuleEnd {
  public type: RuleType.END = RuleType.END;
}

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];
