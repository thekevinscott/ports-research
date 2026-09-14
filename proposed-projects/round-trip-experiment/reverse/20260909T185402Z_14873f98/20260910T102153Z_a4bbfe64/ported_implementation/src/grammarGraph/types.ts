import type { RuleRef } from './ruleRef';

export type ValidInput = string | number | number[];

/** A range is a two-element list of code points, inclusive on both ends. */
export type Range = [number, number];

export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  END: 'end',
} as const;
export type RuleType = (typeof RuleType)[keyof typeof RuleType];

export const ALL_RULE_TYPES: ReadonlySet<string> = new Set<string>(
  Object.values(RuleType),
);

export class RuleChar {
  public readonly type = RuleType.CHAR;
  public value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = [...value];
  }
}

export class RuleCharExclude {
  public readonly type = RuleType.CHAR_EXCLUDE;
  public value: (number | Range)[];

  constructor(value: (number | Range)[]) {
    this.value = [...value];
  }
}

export class RuleEnd {
  public readonly type = RuleType.END;
}

export type Rule = RuleChar | RuleCharExclude | RuleEnd;
export type UnresolvedRule = Rule | RuleRef;
