import type { RuleRef } from './ruleRef.js';

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A range is a two element array of code points, inclusive on both ends.
export type Range = number[];
export type RuleValue = (number | Range)[];

export interface RuleChar {
  type: RuleType.CHAR;
  value: RuleValue;
}

export interface RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE;
  value: RuleValue;
}

export interface RuleEnd {
  type: RuleType.END;
}

export const ruleChar = (value: RuleValue = []): RuleChar => ({
  type: RuleType.CHAR,
  value,
});

export const ruleCharExclude = (value: RuleValue = []): RuleCharExclude => ({
  type: RuleType.CHAR_EXCLUDE,
  value,
});

export const ruleEnd = (): RuleEnd => ({ type: RuleType.END });

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;
export type UnresolvedRule = ResolvedRule | RuleRef;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];
