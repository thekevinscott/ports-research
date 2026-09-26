export const InternalRuleType = {
  CHAR: 'char',
  CHAR_ALT: 'char_alt',
  ALT: 'alt',
  CHAR_NOT: 'char_not',
  CHAR_RNG_UPPER: 'char_rng_upper',
  REFERENCE: 'reference',
  END: 'end',
} as const;

export class InternalRuleDefChar {
  readonly type = InternalRuleType.CHAR;
  value: number[];

  constructor(value: number[] = []) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharNot {
  readonly type = InternalRuleType.CHAR_NOT;
  value: number[];

  constructor(value: number[] = []) {
    this.value = [...value];
  }
}

export class InternalRuleDefCharAlt {
  readonly type = InternalRuleType.CHAR_ALT;

  constructor(readonly value: number) {}
}

export class InternalRuleDefCharRngUpper {
  readonly type = InternalRuleType.CHAR_RNG_UPPER;

  constructor(readonly value: number) {}
}

export class InternalRuleDefReference {
  readonly type = InternalRuleType.REFERENCE;

  constructor(readonly value: number) {}
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

export type InternalRuleDefCharOrAltChar = InternalRuleDefChar | InternalRuleDefCharAlt;

export const isRuleDefAlt = (rule?: InternalRuleDef): rule is InternalRuleDefAlt =>
  rule?.type === InternalRuleType.ALT;

export const isRuleDefRef = (rule?: InternalRuleDef): rule is InternalRuleDefReference =>
  rule?.type === InternalRuleType.REFERENCE;

export const isRuleDefEnd = (rule?: InternalRuleDef): rule is InternalRuleDefEnd =>
  rule?.type === InternalRuleType.END;

export const isRuleDefChar = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  rule?.type === InternalRuleType.CHAR;

export const isRuleDefCharNot = (rule?: InternalRuleDef): rule is InternalRuleDefCharNot =>
  rule?.type === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (rule?: InternalRuleDef): rule is InternalRuleDefCharAlt =>
  rule?.type === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharRngUpper => rule?.type === InternalRuleType.CHAR_RNG_UPPER;
