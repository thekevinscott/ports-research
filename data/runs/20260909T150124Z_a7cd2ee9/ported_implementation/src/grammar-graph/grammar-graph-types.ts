import type { GraphPointer } from './graph-pointer';
import type { Pointers } from './pointers';
import type { RuleRef } from './rule-ref';
import { validateNonEmpty } from '../utils/validate-non-empty';

export interface PrintOpts {
  pointers?: Pointers;
  colorize: (value: string | number, color: string) => string;
  showPosition?: boolean;
}

export type Range = [number, number];

export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  END: 'end',
  REF: 'ref',
} as const;
export type RuleType = (typeof RuleType)[keyof typeof RuleType];

export class RuleEnd {
  type: typeof RuleType.END = RuleType.END;
}

export class RuleChar {
  type: typeof RuleType.CHAR = RuleType.CHAR;
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = [...validateNonEmpty(value)];
  }
}

export class RuleCharExclude {
  type: typeof RuleType.CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE;
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = [...validateNonEmpty(value)];
  }
}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;
