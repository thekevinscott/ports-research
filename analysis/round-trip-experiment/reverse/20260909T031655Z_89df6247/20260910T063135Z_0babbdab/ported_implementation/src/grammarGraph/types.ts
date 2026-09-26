export const RuleType = {
  CHAR: 'char',
  CHAR_EXCLUDE: 'char_exclude',
  END: 'end',
} as const;

export type RuleType = (typeof RuleType)[keyof typeof RuleType];

export const RULE_TYPES: RuleType[] = [
  RuleType.CHAR,
  RuleType.CHAR_EXCLUDE,
  RuleType.END,
];

export type Range = [number, number];
export type RuleCharValue = (number | Range)[];

/** Base for the rules handed back to callers. */
export abstract class BaseRule {
  public abstract readonly type: RuleType;
}

export class RuleChar extends BaseRule {
  public readonly type = RuleType.CHAR;
  public value: RuleCharValue;

  public constructor(value: RuleCharValue = []) {
    super();
    this.value = [...value];
  }
}

export class RuleCharExclude extends BaseRule {
  public readonly type = RuleType.CHAR_EXCLUDE;
  public value: RuleCharValue;

  public constructor(value: RuleCharValue = []) {
    super();
    this.value = [...value];
  }
}

export class RuleEnd extends BaseRule {
  public readonly type = RuleType.END;
}

export type ValueRule = RuleChar | RuleCharExclude;
export type Rule = RuleChar | RuleCharExclude | RuleEnd;
