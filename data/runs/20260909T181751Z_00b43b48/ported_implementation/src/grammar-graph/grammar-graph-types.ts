import { validateNonEmpty } from '../utils/validate-non-empty.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import type { Pointers } from './pointers.js';
import { RuleRef } from './rule-ref.js';
import { RuleType } from './rule-type.js';

export { RuleRef, RuleType };

export type Colorize = (text: string | number, color: string) => string;

export interface PrintOpts {
  pointers?: Pointers;
  colorize: Colorize;
  showPosition?: boolean;
}

export type Range = [number, number];

export abstract class Rule {
  abstract readonly type: RuleType;
}

export abstract class RuleWithListOfIntsOrRanges extends Rule {
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    super();
    // rules coming in are mutated as ranges and alternates are folded into them;
    // take a copy so that callers holding onto the original array are unaffected.
    this.value = validateNonEmpty(value).slice();
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

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;

export type GraphNodeRuleRef = GraphNode<RuleRef>;
