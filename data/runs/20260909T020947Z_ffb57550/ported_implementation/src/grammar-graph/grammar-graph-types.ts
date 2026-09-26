import { validateNonEmpty } from '../utils/validate-non-empty.js';
import type { GraphPointer } from './graph-pointer.js';
import type { Pointers } from './pointers.js';
import type { RuleRef } from './rule-ref.js';
import { RuleType } from './rule-type.js';

export type Colorize = (text: string | number, color: string) => string;

export interface PrintOpts {
  pointers?: Pointers;
  colorize: Colorize;
  showPosition?: boolean;
}

export type Range = [number, number];

export interface RuleChar {
  type: RuleType.CHAR;
  value: (number | Range)[];
}

export interface RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE;
  value: (number | Range)[];
}

export interface RuleEnd {
  type: RuleType.END;
}

export const ruleChar = (value: (number | Range)[]): RuleChar => ({
  type: RuleType.CHAR,
  value: validateNonEmpty([...value]),
});

export const ruleCharExclude = (
  value: (number | Range)[],
): RuleCharExclude => ({
  type: RuleType.CHAR_EXCLUDE,
  value: validateNonEmpty([...value]),
});

export const ruleEnd = (): RuleEnd => ({ type: RuleType.END });

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;
