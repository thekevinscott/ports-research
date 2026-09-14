export const InternalRuleType = {
  CHAR: 'CHAR',
  CHAR_ALT: 'CHAR_ALT',
  CHAR_NOT: 'CHAR_NOT',
  CHAR_RNG_UPPER: 'CHAR_RNG_UPPER',
  REF: 'REF',
  ALT: 'ALT',
  END: 'END',
} as const;
export type InternalRuleType =
  (typeof InternalRuleType)[keyof typeof InternalRuleType];

export class InternalRuleDefChar {
  readonly type = InternalRuleType.CHAR;
  value: number[];

  constructor(value: number[]) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharNot {
  readonly type = InternalRuleType.CHAR_NOT;
  value: number[];

  constructor(value: number[]) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharAlt {
  readonly type = InternalRuleType.CHAR_ALT;
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefCharRngUpper {
  readonly type = InternalRuleType.CHAR_RNG_UPPER;
  value: number;

  constructor(value: number) {
    this.value = value;
  }
}

export class InternalRuleDefReference {
  readonly type = InternalRuleType.REF;
  value: number;

  constructor(value: number) {
    this.value = value;
  }
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
): rule is InternalRuleDefAlt => rule?.type === InternalRuleType.ALT;

export const isRuleDefRef = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefReference => rule?.type === InternalRuleType.REF;

export const isRuleDefEnd = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefEnd => rule?.type === InternalRuleType.END;

export const isRuleDefChar = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefChar => rule?.type === InternalRuleType.CHAR;

export const isRuleDefCharNot = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefCharNot => rule?.type === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefCharAlt => rule?.type === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef | null
): rule is InternalRuleDefCharRngUpper =>
  rule?.type === InternalRuleType.CHAR_RNG_UPPER;
