export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A range is a two element list of code points, inclusive on both ends.
export type Range = [number, number];
export type RuleCharValue = (number | Range)[];

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export class RuleChar {
  type = RuleType.CHAR;
  value: RuleCharValue;

  constructor(value: RuleCharValue) {
    this.value = [...value];
  }
}

export class RuleCharExclude {
  type = RuleType.CHAR_EXCLUDE;
  value: RuleCharValue;

  constructor(value: RuleCharValue) {
    this.value = [...value];
  }
}

export class RuleEnd {
  type = RuleType.END;
}
