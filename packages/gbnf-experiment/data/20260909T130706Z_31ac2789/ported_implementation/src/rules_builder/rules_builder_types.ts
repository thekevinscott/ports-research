/**
 * The internal rule definitions produced by the `RulesBuilder`. These are a
 * flat, linear representation of the grammar; `buildRuleStack` turns them into
 * the stacked rules the graph is built from.
 */
export const InternalRuleType = {
  CHAR: 'char',
  CHAR_ALT: 'char_alt',
  CHAR_NOT: 'char_not',
  CHAR_RNG_UPPER: 'char_rng_upper',
  ALT: 'alt',
  END: 'end',
  RULE_REF: 'rule_ref',
} as const;

export type InternalRuleType = (typeof InternalRuleType)[keyof typeof InternalRuleType];

type Constructor = new (...args: never[]) => unknown;

export abstract class InternalBase {
  abstract readonly type: InternalRuleType;

  equals(other: unknown): boolean {
    return other instanceof (this.constructor as Constructor);
  }
}

export abstract class InternalBaseWithValue<T> extends InternalBase {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  equals(other: unknown): boolean {
    return (
      other instanceof (this.constructor as Constructor) &&
      JSON.stringify((other as InternalBaseWithValue<T>).value) === JSON.stringify(this.value)
    );
  }
}

export abstract class InternalBaseWithInt extends InternalBaseWithValue<number> {}

export abstract class InternalBaseWithListOfInts extends InternalBaseWithValue<number[]> {
  constructor(value: number[] = []) {
    super([...value]);
  }
}

export class InternalRuleDefChar extends InternalBaseWithListOfInts {
  readonly type = InternalRuleType.CHAR;
}

export class InternalRuleDefCharNot extends InternalBaseWithListOfInts {
  readonly type = InternalRuleType.CHAR_NOT;
}

export class InternalRuleDefCharAlt extends InternalBaseWithInt {
  readonly type = InternalRuleType.CHAR_ALT;
}

export class InternalRuleDefCharRngUpper extends InternalBaseWithInt {
  readonly type = InternalRuleType.CHAR_RNG_UPPER;
}

export class InternalRuleDefReference extends InternalBaseWithInt {
  readonly type = InternalRuleType.RULE_REF;
}

export class InternalRuleDefAlt extends InternalBase {
  readonly type = InternalRuleType.ALT;
}

export class InternalRuleDefEnd extends InternalBase {
  readonly type = InternalRuleType.END;
}

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefCharNot
  | InternalRuleDefCharAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefReference
  | InternalRuleDefAlt
  | InternalRuleDefEnd;

export type InternalRuleDefCharOrAltChar = InternalRuleDefChar | InternalRuleDefCharAlt;

export type SymbolIdsMap = Record<string, number>;

export const isRuleDefAlt = (rule: unknown): rule is InternalRuleDefAlt =>
  rule instanceof InternalRuleDefAlt;

export const isRuleDefRef = (rule: unknown): rule is InternalRuleDefReference =>
  rule instanceof InternalRuleDefReference;

export const isRuleDefEnd = (rule: unknown): rule is InternalRuleDefEnd =>
  rule instanceof InternalRuleDefEnd;

export const isRuleDefChar = (rule: unknown): rule is InternalRuleDefChar =>
  rule instanceof InternalRuleDefChar;

export const isRuleDefCharNot = (rule: unknown): rule is InternalRuleDefCharNot =>
  rule instanceof InternalRuleDefCharNot;

export const isRuleDefCharAlt = (rule: unknown): rule is InternalRuleDefCharAlt =>
  rule instanceof InternalRuleDefCharAlt;

export const isRuleDefCharRngUpper = (rule: unknown): rule is InternalRuleDefCharRngUpper =>
  rule instanceof InternalRuleDefCharRngUpper;

export const is_rule_def_alt = isRuleDefAlt;
export const is_rule_def_ref = isRuleDefRef;
export const is_rule_def_end = isRuleDefEnd;
export const is_rule_def_char = isRuleDefChar;
export const is_rule_def_char_not = isRuleDefCharNot;
export const is_rule_def_char_alt = isRuleDefCharAlt;
export const is_rule_def_char_rng_upper = isRuleDefCharRngUpper;
