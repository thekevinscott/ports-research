import { validateNonEmpty } from '../utils/validate-non-empty.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import type { Pointers } from './pointers.js';
import { RuleRef } from './rule-ref.js';

export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  RULE_REF: 'rule_ref',
  END: 'end',
} as const;
export type RuleType = (typeof RuleType)[keyof typeof RuleType];

export type Range = [number, number];

export interface PrintOpts {
  pointers?: Pointers;
  colorize: (value: string | number, color: string) => string;
  showPosition?: boolean;
}

abstract class RuleWithListOfIntsOrRanges {
  value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    // the incoming list is copied so later mutations of the rule that produced
    // it cannot leak into this one.
    this.value = [...value];
  }
}

export class RuleChar extends RuleWithListOfIntsOrRanges {
  type = RuleType.CHAR;
}

export class RuleCharExclude extends RuleWithListOfIntsOrRanges {
  type = RuleType.CHAR_EXCLUDE;
}

export class RuleEnd {
  type = RuleType.END;
}

export { RuleRef, validateNonEmpty };

export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleCharExclude | RuleChar | RuleEnd;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number intended as input (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export type ResolvedGraphPointer = GraphPointer<ResolvedRule>;
export type RootNode = Map<number, GraphNode>;
