/**
 * Rule types exposed by the grammar graph.
 *
 * Port of `gbnf/grammar_graph/types.py`. The Python reference models rules as
 * small classes so that `isinstance` can stand in for structural type guards;
 * here they are plain object literals, discriminated on `type`.
 */

import type { RuleRef } from './rule-ref.js';

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

// A range is a two element list of code points, inclusive on both ends.
export type Range = [number, number];
export type CodePointOrRange = number | Range;

// ValidInput can either be a string, or a number indicating a code point.
// It CANNOT be a number representing a number; a number being a "number" (like "8")
// should be passed in as a string.
export type ValidInput = string | number | number[];

export interface RuleChar {
  type: RuleType.CHAR;
  value: CodePointOrRange[];
}

export interface RuleCharExclude {
  type: RuleType.CHAR_EXCLUDE;
  value: CodePointOrRange[];
}

export interface RuleEnd {
  type: RuleType.END;
}

export const ruleChar = (value: CodePointOrRange[]): RuleChar => ({
  type: RuleType.CHAR,
  value,
});

export const ruleCharExclude = (value: CodePointOrRange[]): RuleCharExclude => ({
  type: RuleType.CHAR_EXCLUDE,
  value,
});

export const ruleEnd = (): RuleEnd => ({ type: RuleType.END });

// RuleRefs should never be exposed to the end user.
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;
export type UnresolvedRule = ResolvedRule | RuleRef;

/** Stable key for a resolved rule. */
export const serializeRule = (rule: ResolvedRule): string => JSON.stringify(rule);
