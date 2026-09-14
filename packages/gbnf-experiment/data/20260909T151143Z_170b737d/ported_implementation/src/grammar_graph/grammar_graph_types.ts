import { RuleRef } from "./rule_ref.ts";
import type { GraphPointer } from "./graph_pointer.ts";
import type { Pointers } from "./pointers.ts";

export { RuleRef };

export interface PrintOpts {
  pointers?: Pointers | Iterable<PrintablePointer>;
  colorize: (text: string | number, color: string) => string;
  show_position?: boolean;
}

/** The shape `print.ts` needs; `GraphNode` satisfies it, and so do test doubles. */
export interface PrintableNode {
  id: string;
  rule: UnresolvedRule;
  next: PrintableNode | null;
  print(opts: PrintOpts): string;
}

export interface PrintablePointer {
  node: PrintableNode;
  print(opts: PrintOpts): string;
}

export type Range = [number, number];

export class Rule {
  equals(other: unknown): boolean {
    return other instanceof (this.constructor as new (...args: never[]) => Rule);
  }

  toString(): string {
    return `${this.constructor.name}()`;
  }

  /** Mirrors the reference's `__dict__` property, used to build JSON keys. */
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
      other instanceof (this.constructor as new (...args: never[]) => RuleWithValue<T>) &&
      deep_equals(this.value, (other as RuleWithValue<T>).value)
    );
  }

  override toString(): string {
    return `${this.constructor.name}(value=${JSON.stringify(this.value)})`;
  }

  override toDict(): Record<string, unknown> {
    return {
      ...super.toDict(),
      value: this.value,
    };
  }
}

export class RuleWithListOfIntsOrRanges extends RuleWithValue<Array<number | Range>> {
  constructor(value: Array<number | Range> = []) {
    // The reference copies the incoming list in `__post_init__`; `build_rule_stack`
    // relies on being able to mutate `value` without touching the caller's array.
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

const deep_equals = (a: unknown, b: unknown): boolean => {
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.length === b.length && a.every((item, idx) => deep_equals(item, b[idx]));
  }
  return a === b;
};
