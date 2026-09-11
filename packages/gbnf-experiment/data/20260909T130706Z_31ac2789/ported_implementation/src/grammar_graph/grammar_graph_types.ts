import { RuleRef } from './rule_ref.ts';
import { RuleType } from './rule_type.ts';

import type { GraphPointer } from './graph_pointer.ts';
import type { Pointers } from './pointers.ts';

export type Colorize = (text: string | number, color: string) => string;

export interface PrintOpts {
  pointers?: Pointers | Set<GraphPointer> | Iterable<GraphPointer>;
  colorize: Colorize;
  show_position?: boolean;
  showPosition?: boolean;
}

export type Range = [number, number];

type Constructor = new (...args: never[]) => unknown;

export abstract class Rule {
  abstract readonly type: RuleType;

  equals(other: unknown): boolean {
    return other instanceof (this.constructor as Constructor);
  }

  toJSON(): { type: RuleType } {
    return {
      type: this.type,
    };
  }
}

export abstract class RuleWithValue<T> extends Rule {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  equals(other: unknown): boolean {
    return (
      other instanceof (this.constructor as Constructor) &&
      JSON.stringify((other as RuleWithValue<T>).value) === JSON.stringify(this.value)
    );
  }

  toJSON(): { type: RuleType; value: T } {
    return {
      ...super.toJSON(),
      value: this.value,
    };
  }
}

export abstract class RuleWithListOfIntsOrRanges extends RuleWithValue<(number | Range)[]> {
  constructor(value: (number | Range)[] = []) {
    super([...value]);
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

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export { RuleRef, RuleType };
