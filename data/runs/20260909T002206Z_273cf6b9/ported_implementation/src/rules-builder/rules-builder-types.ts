export class InternalRuleDefWithNumericValue {
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

export class InternalBase {}

export class InternalBaseWithValue {
  value: unknown;

  constructor(value: unknown) {
    this.value = value;
  }
}

export class InternalBaseWithInt extends InternalBaseWithValue {
  declare value: number;

  constructor(value: number) {
    super(value);
  }
}

export class InternalBaseWithListOfInts extends InternalBaseWithValue {
  declare value: number[];

  constructor(value: number[] = []) {
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
  | InternalRuleDefWithNumericValue
  | InternalRuleDefWithoutValue
  | InternalRuleDefAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefCharAlt;

export type InternalRuleDefCharOrAltChar = InternalRuleDefChar | InternalRuleDefCharAlt;

export type SymbolIdsRecord = Record<string, number>;

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
