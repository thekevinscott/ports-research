import type { Pointers } from './pointers.js';
import type { RuleRef } from './ruleRef.js';

export type Colorize = (text: string | number, color: string) => string;

export interface PrintOpts {
  pointers?: Pointers;
  colorize: Colorize;
  show_position?: boolean;
}

export type Range = [number, number];

export type RuleDict = { type: string; value?: unknown };

export abstract class Rule {
  abstract get type(): string;

  equals(other: unknown): boolean {
    return other instanceof Rule && other.constructor === this.constructor;
  }

  toDict(): RuleDict {
    return { type: this.type };
  }

  toJSON(): RuleDict {
    return this.toDict();
  }

  toString(): string {
    return `${this.type}()`;
  }
}

export abstract class RuleWithValue<T> extends Rule {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  override equals(other: unknown): boolean {
    return (
      other instanceof RuleWithValue &&
      other.constructor === this.constructor &&
      JSON.stringify(this.value) === JSON.stringify(other.value)
    );
  }

  override toDict(): RuleDict {
    return { ...super.toDict(), value: this.value };
  }

  override toString(): string {
    return `${this.type}(value=${JSON.stringify(this.value)})`;
  }
}

export abstract class RuleWithListOfIntsOrRanges extends RuleWithValue<(number | Range)[]> {
  constructor(value: (number | Range)[] = []) {
    // the reference implementation copies the incoming list so that later mutation of the
    // rule's value cannot be observed by the caller.
    super([...value]);
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {
  get type(): 'RuleChar' {
    return 'RuleChar';
  }
}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {
  get type(): 'RuleCharExclude' {
    return 'RuleCharExclude';
  }
}

export class RuleEnd extends Rule {
  get type(): 'RuleEnd' {
    return 'RuleEnd';
  }
}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;
