export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A range is a two element [start, end] pair of code points.
export type Range = [number, number];
export type RuleValue = number | Range;
// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number"
// (like "8") should be passed in as a string.
export type ValidInput = string | number | number[];

export interface RuleCharJSON { type: RuleType.CHAR; value: RuleValue[] }
export interface RuleCharExcludeJSON { type: RuleType.CHAR_EXCLUDE; value: RuleValue[] }
export interface RuleEndJSON { type: RuleType.END }
export type RuleJSON = RuleCharJSON | RuleCharExcludeJSON | RuleEndJSON;

/**
 * Base class for the rules exposed to consumers of a `ParseState`.
 *
 * Rules are compared by reference; the graph relies on that to dedupe and to
 * group pointers.
 */
export abstract class AbstractRule {
  abstract readonly type: RuleType;

  abstract toJSON(): RuleJSON;

  serialize(): string {
    return JSON.stringify(this.toJSON());
  }
}

export abstract class RuleWithValue extends AbstractRule {
  value: RuleValue[];

  constructor(value: RuleValue[] = []) {
    super();
    this.value = value.map(v => (Array.isArray(v) ? ([...v] as Range) : v));
  }

  toString(): string {
    return `${this.constructor.name}(${JSON.stringify(this.value)})`;
  }
}

export class RuleChar extends RuleWithValue {
  readonly type = RuleType.CHAR;

  toJSON(): RuleCharJSON {
    return { type: this.type, value: this.value };
  }
}

export class RuleCharExclude extends RuleWithValue {
  readonly type = RuleType.CHAR_EXCLUDE;

  toJSON(): RuleCharExcludeJSON {
    return { type: this.type, value: this.value };
  }
}

export class RuleEnd extends AbstractRule {
  readonly type = RuleType.END;

  toJSON(): RuleEndJSON {
    return { type: this.type };
  }

  toString(): string {
    return 'RuleEnd()';
  }
}

export type Rule = RuleChar | RuleCharExclude | RuleEnd;
