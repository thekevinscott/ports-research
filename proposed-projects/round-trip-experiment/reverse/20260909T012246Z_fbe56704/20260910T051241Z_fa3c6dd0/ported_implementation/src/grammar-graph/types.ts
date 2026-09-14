import type { RuleRef } from './rule-ref.ts';

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

/** A range of code points, inclusive on both ends. */
export type Range = [number, number];

/**
 * ValidInput can either be a string, or a number indicating a code point.
 * It CANNOT be a number representing a number; a number being a "number" (like "8")
 * should be passed in as a string.
 */
export type ValidInput = string | number | number[];

export class RuleChar {
  type: RuleType.CHAR = RuleType.CHAR;
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = value;
  }
}

export class RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE;
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = value;
  }
}

export class RuleEnd {
  type: RuleType.END = RuleType.END;
}

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;
export type UnresolvedRule = ResolvedRule | RuleRef;
