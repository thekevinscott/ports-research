export type ValidInput = string | number | number[];

// A range is a two element array of code points, inclusive on both ends.
export type Range = [number, number];
export type CharValue = (number | Range)[];

export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  END: 'end',
} as const;

export type RuleType = (typeof RuleType)[keyof typeof RuleType];

export class RuleChar {
  type: typeof RuleType.CHAR = RuleType.CHAR;
  value: CharValue;

  constructor(value: CharValue) {
    this.value = [...value];
  }

  toString(): string {
    return `RuleChar(${JSON.stringify(this.value)})`;
  }
}

export class RuleCharExclude {
  type: typeof RuleType.CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE;
  value: CharValue;

  constructor(value: CharValue) {
    this.value = [...value];
  }

  toString(): string {
    return `RuleCharExclude(${JSON.stringify(this.value)})`;
  }
}

export class RuleEnd {
  type: typeof RuleType.END = RuleType.END;

  toString(): string {
    return 'RuleEnd()';
  }
}

export type Rule = RuleChar | RuleCharExclude | RuleEnd;
