/**
 * The intermediate ("internal") rule representation produced by the RulesBuilder,
 * before it is folded into the graph's rule stacks.
 *
 * Each class is a distinct nominal type: the type guards below rely on the
 * prototype chain, exactly as the reference implementation relies on `isinstance`.
 */

export class InternalRuleDefWithNumericValue {
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

/** Base for rules that carry no value; equality is "same class". */
export class InternalBase {}

/** Base for rules that carry a single integer value. */
export class InternalBaseWithInt {
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

/** Base for rules that carry a list of integer values; the list is copied on construction. */
export class InternalBaseWithListOfInts {
  value: number[];

  constructor(value: number[] = []) {
    this.value = [...value];
  }
}

export class InternalRuleDefChar extends InternalBaseWithListOfInts {}

export class InternalRuleDefCharNot extends InternalBaseWithListOfInts {}

export class InternalRuleDefCharAlt extends InternalBaseWithInt {}

export class InternalRuleDefCharRngUpper extends InternalBaseWithInt {}

export class InternalRuleDefReference extends InternalBaseWithInt {}

export class InternalRuleDefAlt extends InternalBase {}

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
