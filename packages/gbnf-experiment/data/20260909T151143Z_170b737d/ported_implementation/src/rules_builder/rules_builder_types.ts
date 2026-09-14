export class InternalBase {
  equals(other: unknown): boolean {
    return other instanceof (this.constructor as new (...args: never[]) => InternalBase);
  }
}

export class InternalBaseWithValue<T = unknown> extends InternalBase {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  override equals(other: unknown): boolean {
    return (
      other instanceof (this.constructor as new (...args: never[]) => InternalBaseWithValue<T>) &&
      values_equal(this.value, (other as InternalBaseWithValue<T>).value)
    );
  }
}

export class InternalBaseWithInt extends InternalBaseWithValue<number> {}

export class InternalBaseWithListOfInts extends InternalBaseWithValue<number[]> {
  constructor(value: number[] = []) {
    // Mirrors the reference's `__post_init__`, which copies the incoming list.
    super([...value]);
  }
}

export class InternalRuleDefChar extends InternalBaseWithListOfInts {}

export class InternalRuleDefCharAlt extends InternalBaseWithInt {}

export class InternalRuleDefAlt extends InternalBase {}

export class InternalRuleDefCharNot extends InternalBaseWithListOfInts {}

export class InternalRuleDefCharRngUpper extends InternalBaseWithInt {}

export class InternalRuleDefReference extends InternalBaseWithInt {}

export class InternalRuleDefEnd extends InternalBase {}

export class InternalRuleDefWithoutValue extends InternalBase {}

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefEnd
  | InternalRuleDefReference
  | InternalRuleDefCharNot
  | InternalRuleDefWithoutValue
  | InternalRuleDefAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefCharAlt;

export type InternalRuleDefCharOrAltChar = InternalRuleDefChar | InternalRuleDefCharAlt;

export const is_rule_def_alt = (rule: unknown): rule is InternalRuleDefAlt =>
  rule instanceof InternalRuleDefAlt;

export const is_rule_def_ref = (rule: unknown): rule is InternalRuleDefReference =>
  rule instanceof InternalRuleDefReference;

export const is_rule_def_end = (rule: unknown): rule is InternalRuleDefEnd =>
  rule instanceof InternalRuleDefEnd;

export const is_rule_def_char = (rule: unknown): rule is InternalRuleDefChar =>
  rule instanceof InternalRuleDefChar;

export const is_rule_def_char_not = (rule: unknown): rule is InternalRuleDefCharNot =>
  rule instanceof InternalRuleDefCharNot;

export const is_rule_def_char_alt = (rule: unknown): rule is InternalRuleDefCharAlt =>
  rule instanceof InternalRuleDefCharAlt;

export const is_rule_def_char_rng_upper = (
  rule: unknown,
): rule is InternalRuleDefCharRngUpper => rule instanceof InternalRuleDefCharRngUpper;

const values_equal = (a: unknown, b: unknown): boolean => {
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.length === b.length && a.every((item, idx) => values_equal(item, b[idx]));
  }
  return a === b;
};
