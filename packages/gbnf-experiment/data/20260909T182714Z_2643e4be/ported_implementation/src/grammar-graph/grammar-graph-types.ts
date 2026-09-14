import type { Pointers } from "./pointers.js";
import type { GraphPointer } from "./graph-pointer.js";
import type { RuleRef } from "./rule-ref.js";

export interface PrintOpts {
  pointers: Pointers;
  colorize: (text: string | number, color: string) => string;
  showPosition: boolean;
}

export type Range = [number, number];

// Renders values the way Python's `repr` does, so reprs match the reference.
const formatValue = (value: unknown): string =>
  Array.isArray(value)
    ? `[${value.map(formatValue).join(", ")}]`
    : String(value);

export class Rule {
  /**
   * The reference implementation exposes the class name as `type` through its
   * `__dict__` property.
   */
  get type(): string {
    return this.constructor.name;
  }

  equals(other: unknown): boolean {
    return other instanceof this.constructor;
  }

  toString(): string {
    return `${this.constructor.name}()`;
  }

  toDict(): Record<string, unknown> {
    return {
      type: this.constructor.name,
    };
  }
}

export class RuleWithValue<T = unknown> extends Rule {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  override equals(other: unknown): boolean {
    return (
      other instanceof this.constructor &&
      JSON.stringify((other as RuleWithValue<T>).value) ===
        JSON.stringify(this.value)
    );
  }

  override toString(): string {
    return `${this.constructor.name}(value=${formatValue(this.value)})`;
  }

  override toDict(): Record<string, unknown> {
    return {
      ...super.toDict(),
      value: this.value,
    };
  }
}

export class RuleWithListOfIntsOrRanges extends RuleWithValue<
  (number | Range)[]
> {
  constructor(value: (number | Range)[] = []) {
    // the reference implementation copies the incoming list
    super([...value]);
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {}

export class RuleEnd extends Rule {}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;
