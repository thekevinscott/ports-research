import type { GraphPointer } from './graph-pointer.ts';
import type { Pointers } from './pointers.ts';
import { RuleRef } from './rule-ref.ts';

export type Colorize = (text: string | number, color: string) => string;

export interface PrintOpts {
  pointers?: Pointers;
  colorize: Colorize;
  show_position?: boolean;
}

export type Range = [number, number];

export type RuleDict = { type: string; value?: unknown };

export class Rule {
  readonly type: string = 'Rule';

  equals(other: unknown): boolean {
    return other instanceof (this.constructor as new (...args: never[]) => unknown);
  }

  toString(): string {
    return `${this.type}()`;
  }

  /** Mirrors the reference implementation's `__dict__`, used for serializing a rule. */
  get dict(): RuleDict {
    return {
      type: this.type,
    };
  }
}

export class RuleWithValue extends Rule {
  override readonly type: string = 'RuleWithValue';
  value: unknown;

  constructor(value: unknown) {
    super();
    this.value = value;
  }

  override equals(other: unknown): boolean {
    return super.equals(other) && valuesAreEqual(this.value, (other as RuleWithValue).value);
  }

  override toString(): string {
    return `${this.type}(value=${JSON.stringify(this.value)})`;
  }

  override get dict(): RuleDict {
    return {
      ...super.dict,
      value: this.value,
    };
  }
}

export class RuleWithListOfIntsOrRanges extends RuleWithValue {
  override readonly type: string = 'RuleWithListOfIntsOrRanges';
  declare value: (number | Range)[];

  constructor(value: (number | Range)[] = []) {
    super([...value]);
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {
  override readonly type = 'RuleChar';
}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {
  override readonly type = 'RuleCharExclude';
}

export class RuleEnd extends Rule {
  override readonly type = 'RuleEnd';
}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;

const valuesAreEqual = (left: unknown, right: unknown): boolean => {
  if (Array.isArray(left) && Array.isArray(right)) {
    return left.length === right.length && left.every((value, idx) => valuesAreEqual(value, right[idx]));
  }
  return left === right;
};

export { RuleRef };
