import type { RuleRef } from './rule-ref.ts';

export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  END: 'end',
} as const;
export type RuleType = (typeof RuleType)[keyof typeof RuleType];

/** An inclusive `[start, end]` pair of code points. */
export type Range = [number, number];
export type RangeOrCodePoint = number | Range;

export interface RuleChar {
  type: typeof RuleType.CHAR;
  value: RangeOrCodePoint[];
}

export interface RuleCharExclude {
  type: typeof RuleType.CHAR_EXCLUDE;
  value: RangeOrCodePoint[];
}

export interface RuleEnd {
  type: typeof RuleType.END;
}

/** `RuleRef`s should never be exposed to the end user. */
export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

/**
 * `ValidInput` can either be a string, or a number indicating a code point.
 * It CANNOT be a number representing a number; a number being a "number" (like "8")
 * should be passed in as a string.
 */
export type ValidInput = string | number | number[];
