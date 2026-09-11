import type { GraphPointer } from './graph-pointer.js';
import type { Pointers } from './pointers.js';
import type { RuleRef } from './rule-ref.js';

export type Colorize = (text: string | number, color: string) => string;

export interface PrintOpts {
  pointers?: Pointers;
  colorize: Colorize;
  showPosition?: boolean;
}

export type Range = [number, number];

export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  END: 'end',
  REF: 'ref',
} as const;

export type RuleTypeValue = (typeof RuleType)[keyof typeof RuleType];

export class RuleChar {
  readonly type = RuleType.CHAR;
  value: (number | Range)[];

  constructor(value: (number | Range)[] = []) {
    this.value = [...value];
  }
}

export class RuleCharExclude {
  readonly type = RuleType.CHAR_EXCLUDE;
  value: (number | Range)[];

  constructor(value: (number | Range)[] = []) {
    this.value = [...value];
  }
}

export class RuleEnd {
  readonly type = RuleType.END;
}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;
