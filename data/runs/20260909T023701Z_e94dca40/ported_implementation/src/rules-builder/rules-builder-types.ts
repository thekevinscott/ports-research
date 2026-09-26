export enum InternalRuleType {
  CHAR = 'char',
  CHAR_ALT = 'char_alt',
  ALT = 'alt',
  CHAR_NOT = 'char_not',
  CHAR_RNG_UPPER = 'char_rng_upper',
  REFERENCE = 'reference',
  END = 'end',
}

export class InternalRuleDefChar {
  type = InternalRuleType.CHAR as const;
  value: number[];

  constructor(value: number[] = []) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharAlt {
  type = InternalRuleType.CHAR_ALT as const;
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefAlt {
  type = InternalRuleType.ALT as const;
}

export class InternalRuleDefCharNot {
  type = InternalRuleType.CHAR_NOT as const;
  value: number[];

  constructor(value: number[] = []) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharRngUpper {
  type = InternalRuleType.CHAR_RNG_UPPER as const;
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefReference {
  type = InternalRuleType.REFERENCE as const;
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefEnd {
  type = InternalRuleType.END as const;
}

export type InternalRuleDef =
  | InternalRuleDefChar
  | InternalRuleDefCharAlt
  | InternalRuleDefAlt
  | InternalRuleDefCharNot
  | InternalRuleDefCharRngUpper
  | InternalRuleDefReference
  | InternalRuleDefEnd;

export type InternalRuleDefCharOrAltChar =
  | InternalRuleDefChar
  | InternalRuleDefCharAlt;

export const isRuleDefAlt = (
  rule?: InternalRuleDef | null,
): rule is InternalRuleDefAlt => rule instanceof InternalRuleDefAlt;

export const isRuleDefRef = (
  rule?: InternalRuleDef | null,
): rule is InternalRuleDefReference => rule instanceof InternalRuleDefReference;

export const isRuleDefEnd = (
  rule?: InternalRuleDef | null,
): rule is InternalRuleDefEnd => rule instanceof InternalRuleDefEnd;

export const isRuleDefChar = (
  rule?: InternalRuleDef | null,
): rule is InternalRuleDefChar => rule instanceof InternalRuleDefChar;

export const isRuleDefCharNot = (
  rule?: InternalRuleDef | null,
): rule is InternalRuleDefCharNot => rule instanceof InternalRuleDefCharNot;

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef | null,
): rule is InternalRuleDefCharAlt => rule instanceof InternalRuleDefCharAlt;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef | null,
): rule is InternalRuleDefCharRngUpper =>
  rule instanceof InternalRuleDefCharRngUpper;
