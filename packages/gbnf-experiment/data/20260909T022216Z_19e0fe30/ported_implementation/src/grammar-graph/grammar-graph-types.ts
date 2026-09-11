import type { GraphPointer } from './graph-pointer.js';
import type { Pointers } from './pointers.js';
import { RuleType } from './rule-type.js';
import { RuleRef } from './rule-ref.js';

export interface PrintOpts {
  pointers?: Pointers;
  colorize: (text: string | number, color: string) => string;
  showPosition?: boolean;
}

export type Range = [number, number];

export abstract class Rule {
  abstract readonly type: RuleType;

  equals(other: unknown): boolean {
    return (
      other instanceof Rule &&
      JSON.stringify(this.toJSON()) === JSON.stringify(other.toJSON())
    );
  }

  toJSON(): { type: RuleType; value?: (number | Range)[] } {
    return { type: this.type };
  }

  toString(): string {
    return JSON.stringify(this.toJSON());
  }
}

export abstract class RuleWithListOfIntsOrRanges extends Rule {
  value: (number | Range)[];

  constructor(value: (number | Range)[] = []) {
    super();
    // the value is copied so that later mutation of the source array cannot
    // leak into the rule.
    this.value = [...value];
  }

  override toJSON(): { type: RuleType; value: (number | Range)[] } {
    return { type: this.type, value: this.value };
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

export { RuleType, RuleRef };
