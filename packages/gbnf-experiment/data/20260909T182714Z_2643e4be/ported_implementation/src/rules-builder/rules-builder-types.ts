/**
 * Internal (linear) rule definitions produced by the RulesBuilder, before they
 * are folded into a stack of paths by `buildRuleStack`.
 */

export class InternalBase {
  equals(other: unknown): boolean {
    return other instanceof this.constructor;
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
      other instanceof this.constructor &&
      JSON.stringify((other as InternalBaseWithValue<T>).value) ===
        JSON.stringify(this.value)
    );
  }
}

export class InternalBaseWithInt extends InternalBaseWithValue<number> {}

export class InternalBaseWithListOfInts extends InternalBaseWithValue<number[]> {
  constructor(value: number[] = []) {
    // the reference implementation copies the incoming list
    super([...value]);
  }
}

export class InternalRuleDefWithNumericValue extends InternalBaseWithInt {}

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
  | InternalRuleDefWithNumericValue
  | InternalRuleDefWithoutValue
  | InternalRuleDefAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefCharAlt;

export type InternalRuleDefCharOrAltChar =
  | InternalRuleDefChar
  | InternalRuleDefCharAlt;

export type SymbolIds = Record<string, number>;

export const isRuleDefAlt = (rule: unknown): rule is InternalRuleDefAlt =>
  rule instanceof InternalRuleDefAlt;

export const isRuleDefRef = (rule: unknown): rule is InternalRuleDefReference =>
  rule instanceof InternalRuleDefReference;

export const isRuleDefEnd = (rule: unknown): rule is InternalRuleDefEnd =>
  rule instanceof InternalRuleDefEnd;

export const isRuleDefChar = (rule: unknown): rule is InternalRuleDefChar =>
  rule instanceof InternalRuleDefChar;

export const isRuleDefCharNot = (
  rule: unknown,
): rule is InternalRuleDefCharNot => rule instanceof InternalRuleDefCharNot;

export const isRuleDefCharAlt = (
  rule: unknown,
): rule is InternalRuleDefCharAlt => rule instanceof InternalRuleDefCharAlt;

export const isRuleDefCharRngUpper = (
  rule: unknown,
): rule is InternalRuleDefCharRngUpper =>
  rule instanceof InternalRuleDefCharRngUpper;
