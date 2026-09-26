import type { Pointers } from './pointers.ts';
import type { RuleRef } from './rule-ref.ts';

export type Range = [number, number];

export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  END: 'end',
  REF: 'ref',
} as const;
export type RuleType = (typeof RuleType)[keyof typeof RuleType];

export abstract class RuleWithListOfIntsOrRanges {
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = [...value];
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {
  readonly type = RuleType.CHAR;
}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {
  readonly type = RuleType.CHAR_EXCLUDE;
}

export class RuleEnd {
  readonly type = RuleType.END;
}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export interface PrintOpts {
  pointers?: Pointers;
  colorize: (value: string | number, color: string) => string;
  showPosition?: boolean;
}
