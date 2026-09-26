import { repr } from '../utils/repr.ts';
import type { GraphPointer } from './graphPointer.ts';
import type { Pointers } from './pointers.ts';
import { RuleRef } from './ruleRef.ts';

export type Colorize = (text: string | number, color: string) => string;

export interface PrintOpts {
  pointers?: Pointers;
  colorize: Colorize;
  showPosition?: boolean;
}

export type Range = [number, number];

export class Rule {
  get type(): string {
    return 'Rule';
  }

  toDict(): Record<string, unknown> {
    return { type: this.type };
  }

  toRepr(): string {
    return `${this.type}()`;
  }
}

export class RuleWithValue<T> extends Rule {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  override toDict(): Record<string, unknown> {
    return { ...super.toDict(), value: this.value };
  }

  override toRepr(): string {
    return `${this.type}(value=${repr(this.value)})`;
  }
}

export class RuleWithListOfIntsOrRanges extends RuleWithValue<(number | Range)[]> {
  constructor(value: (number | Range)[] = []) {
    super([...value]);
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {
  override get type(): string {
    return 'RuleChar';
  }
}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {
  override get type(): string {
    return 'RuleCharExclude';
  }
}

export class RuleEnd extends Rule {
  override get type(): string {
    return 'RuleEnd';
  }
}

export { RuleRef };

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
