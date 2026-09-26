import type { RuleRef } from './rule-ref.js';

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

// a Range is a two element list of code points, inclusive on both ends.
export type Range = [number, number];

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

export type RuleChar = {
  type: RuleType.CHAR;
  value: (number | Range)[];
};

export type RuleCharExclude = {
  type: RuleType.CHAR_EXCLUDE;
  value: (number | Range)[];
};

export type RuleEnd = {
  type: RuleType.END;
};

/** The rules handed back to the caller. */
export type Rule = RuleChar | RuleCharExclude | RuleEnd;

/** A rule as stored in the graph, which may still be an unresolved reference. */
export type UnresolvedRule = Rule | RuleRef;
