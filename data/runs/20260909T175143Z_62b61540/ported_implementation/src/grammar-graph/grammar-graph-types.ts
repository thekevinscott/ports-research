import type { GraphPointer } from './graph-pointer';
import type { Pointers } from './pointers';
import type { RuleRef } from './rule-ref';

export interface PrintOpts {
  pointers?: Pointers;
  colorize: (value: string | number, color: string) => string;
  showPosition?: boolean;
}

export type Range = [number, number];

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
  REF = 'ref',
}

export class RuleChar {
  type = RuleType.CHAR as const;
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = [...value];
  }
}

export class RuleCharExclude {
  type = RuleType.CHAR_EXCLUDE as const;
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = [...value];
  }
}

export class RuleEnd {
  type = RuleType.END as const;
}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;
