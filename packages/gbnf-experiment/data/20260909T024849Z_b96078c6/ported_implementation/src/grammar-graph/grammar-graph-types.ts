import type { GraphPointer } from "./graph-pointer.ts";
import type { Pointers } from "./pointers.ts";
import type { RuleRef } from "./rule-ref.ts";

export interface PrintOpts {
  pointers?: Pointers | Iterable<GraphPointer>;
  colorize: (text: string | number, color: string) => string;
  showPosition?: boolean;
  /** snake_case spelling used by the reference implementation. */
  show_position?: boolean;
}

export type Range = [number, number];

/** The value carried by a char rule: code points and/or inclusive ranges. */
export type RuleCharValue = (number | Range)[];

export class Rule {
  get type(): string {
    return "Rule";
  }

  /** Mirrors the reference implementation's `Rule.__dict__`. */
  toJSON(): Record<string, unknown> {
    return { type: this.type };
  }

  toString(): string {
    return `${this.type}()`;
  }
}

export class RuleWithValue extends Rule {
  value: unknown;

  constructor(value: unknown) {
    super();
    this.value = value;
  }

  toJSON(): Record<string, unknown> {
    return { ...super.toJSON(), value: this.value };
  }

  toString(): string {
    return `${this.type}(value=${JSON.stringify(this.value)})`;
  }
}

export class RuleWithListOfIntsOrRanges extends RuleWithValue {
  declare value: RuleCharValue;

  constructor(value: RuleCharValue = []) {
    super([...value]);
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {
  get type(): string {
    return "RuleChar";
  }
}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {
  get type(): string {
    return "RuleCharExclude";
  }
}

export class RuleEnd extends Rule {
  get type(): string {
    return "RuleEnd";
  }
}

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

/** RuleRefs should never be exposed to the end user. */
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;

/**
 * ValidInput can either be a string, or a number indicating a code point.
 * It CANNOT be a number representing a number; a number intended as input
 * (like "8") should be passed in as a string.
 */
export type ValidInput = string | number | number[];
