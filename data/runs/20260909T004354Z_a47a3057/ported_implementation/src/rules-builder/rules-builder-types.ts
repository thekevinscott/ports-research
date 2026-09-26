export class InternalRuleDefChar {
  value: number[];
  constructor(value: number[]) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharNot {
  value: number[];
  constructor(value: number[]) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharAlt {
  value: number;
  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefCharRngUpper {
  value: number;
  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefReference {
  value: number;
  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefAlt {}

export class InternalRuleDefEnd {}

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefCharNot
  | InternalRuleDefCharAlt
  | InternalRuleDefCharRngUpper
  | InternalRuleDefReference
  | InternalRuleDefAlt
  | InternalRuleDefEnd;

export type InternalRuleDefCharOrAltChar =
  | InternalRuleDefChar
  | InternalRuleDefCharAlt;

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

export type SymbolIdsMap = Map<string, number>;
