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

export class Rule {
  /** Mirrors the reference's use of the class name as the serialized rule type. */
  get type(): string {
    return this.constructor.name;
  }

  /** The reference implementation's `__dict__`; used for serialization and equality keys. */
  toDict(): Record<string, unknown> {
    return { type: this.type };
  }

  toString(): string {
    return `${this.type}()`;
  }
}

export class RuleWithValue<T = unknown> extends Rule {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  override toDict(): Record<string, unknown> {
    return { ...super.toDict(), value: this.value };
  }

  override toString(): string {
    return `${this.type}(value=${JSON.stringify(this.value)})`;
  }
}

export class RuleWithListOfIntsOrRanges extends RuleWithValue<(number | Range)[]> {
  constructor(value: (number | Range)[] = []) {
    super([...value]);
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {}

export class RuleEnd extends Rule {}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

/**
 * ValidInput can either be a string, or a number indicating a code point.
 * It CANNOT be a number representing a number; a number intended as input (like "8")
 * should be passed in as a string.
 */
export type ValidInput = string | number | number[];

/** RuleRefs should never be exposed to the end user. */
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;

export { RuleRef };
