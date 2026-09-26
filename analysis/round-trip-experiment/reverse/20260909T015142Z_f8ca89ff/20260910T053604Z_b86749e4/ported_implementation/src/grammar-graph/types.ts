import type { GenericSet } from './generic-set';
import type { GraphPointer } from './graph-pointer';
import { RuleRef } from './rule-ref';

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

/** A `Range` is a pair of code points, inclusive on both ends. */
export type Range = [number, number];

export type RuleCharValue = number | Range;

export class RuleChar {
  public type: RuleType.CHAR = RuleType.CHAR;
  public value: RuleCharValue[];

  constructor(value: RuleCharValue[] = []) {
    this.value = value;
  }
}

export class RuleCharExclude {
  public type: RuleType.CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE;
  public value: RuleCharValue[];

  constructor(value: RuleCharValue[] = []) {
    this.value = value;
  }
}

export class RuleEnd {
  public type: RuleType.END = RuleType.END;
}

export type Rule = RuleChar | RuleCharExclude | RuleEnd;

// RuleRefs are never exposed to the end user.
export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export type Pointers = GenericSet<GraphPointer, string>;

export { RuleRef };
