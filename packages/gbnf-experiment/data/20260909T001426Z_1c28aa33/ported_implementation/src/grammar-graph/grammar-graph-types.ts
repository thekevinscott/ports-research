import type { GraphPointer } from './graph-pointer';
import type { Pointers } from './pointers';
import { RuleRef } from './rule-ref';

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
}

export abstract class Rule {
  abstract readonly type: RuleType;
}

export abstract class RuleWithListOfIntsOrRanges extends Rule {
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    super();
    // copied so that mutating this rule's value never reaches back into the source list.
    this.value = value.slice();
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {
  readonly type = RuleType.CHAR;
}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {
  readonly type = RuleType.CHAR_EXCLUDE;
}

export class RuleEnd extends Rule {
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

export { RuleRef };
