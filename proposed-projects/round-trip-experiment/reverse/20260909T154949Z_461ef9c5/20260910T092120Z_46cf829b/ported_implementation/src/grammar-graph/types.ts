import type { RuleRef } from './rule-ref.js';

export enum RuleType {
  CHAR = 'char',
  CHAR_EXCLUDE = 'char_exclude',
  END = 'end',
}

export type Range = [number, number];
export type CodePointOrRange = number | Range;

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

// RuleRefs should never be exposed to the end user.
export type UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd;
export type ResolvedRule = RuleChar | RuleCharExclude | RuleEnd;

export type { ValidInput } from '../valid-input.js';
