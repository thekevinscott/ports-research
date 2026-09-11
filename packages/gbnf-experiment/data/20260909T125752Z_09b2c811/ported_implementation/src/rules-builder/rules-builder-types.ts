export const InternalRuleType = {
  CHAR: 'char',
  CHAR_ALT: 'char_alt',
  ALT: 'alt',
  CHAR_NOT: 'char_not',
  CHAR_RNG_UPPER: 'char_rng_upper',
  REFERENCE: 'reference',
  END: 'end',
} as const;

export type InternalRuleType =
  (typeof InternalRuleType)[keyof typeof InternalRuleType];

export class InternalRuleDefChar {
  readonly type = InternalRuleType.CHAR;
  value: number[];

  constructor(value: number[] = []) {
    this.value = value.slice();
  }
}

export class InternalRuleDefCharNot {
  readonly type = InternalRuleType.CHAR_NOT;
  value: number[];

  constructor(value: number[] = []) {
    this.value = value.slice();
  }
}

export class InternalRuleDefCharAlt {
  readonly type = InternalRuleType.CHAR_ALT;

  constructor(public value: number) {}
}

export class InternalRuleDefCharRngUpper {
  readonly type = InternalRuleType.CHAR_RNG_UPPER;

  constructor(public value: number) {}
}

export class InternalRuleDefReference {
  readonly type = InternalRuleType.REFERENCE;

  constructor(public value: number) {}
}

export class InternalRuleDefAlt {
  readonly type = InternalRuleType.ALT;
}

export class InternalRuleDefEnd {
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

export type InternalRuleDefCharOrAltChar =
  | InternalRuleDefChar
  | InternalRuleDefCharAlt;

export const isRuleDefAlt = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefAlt => rule instanceof InternalRuleDefAlt;

export const isRuleDefRef = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefReference => rule instanceof InternalRuleDefReference;

export const isRuleDefEnd = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefEnd => rule instanceof InternalRuleDefEnd;

export const isRuleDefChar = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefChar => rule instanceof InternalRuleDefChar;

export const isRuleDefCharNot = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefCharNot => rule instanceof InternalRuleDefCharNot;

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefCharAlt => rule instanceof InternalRuleDefCharAlt;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefCharRngUpper =>
  rule instanceof InternalRuleDefCharRngUpper;
