export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A `Range` is a two element `[start, end]` pair of code points.
export type Range = [number, number];

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export type CharValue = (number | Range)[];

export class RuleChar {
  public type: RuleType.CHAR = RuleType.CHAR;
  public value: CharValue;

  constructor(value: CharValue) {
    this.value = value;
  }
}

export class RuleCharExclude {
  public type: RuleType.CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE;
  public value: CharValue;

  constructor(value: CharValue) {
    this.value = value;
  }
}

export class RuleEnd {
  public type: RuleType.END = RuleType.END;
}
