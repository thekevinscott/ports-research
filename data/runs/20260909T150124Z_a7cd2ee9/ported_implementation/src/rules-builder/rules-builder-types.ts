import { validateNonEmpty } from '../utils/validate-non-empty';

export const InternalRuleType = {
  CHAR: 'char',
  CHAR_RNG_UPPER: 'char_rng_upper',
  CHAR_ALT: 'char_alt',
  CHAR_NOT: 'char_not',
  ALT: 'alt',
  END: 'end',
  REF: 'ref',
} as const;
export type InternalRuleType =
  (typeof InternalRuleType)[keyof typeof InternalRuleType];

export interface InternalRuleDefChar {
  type: typeof InternalRuleType.CHAR;
  value: number[];
}

export interface InternalRuleDefCharNot {
  type: typeof InternalRuleType.CHAR_NOT;
  value: number[];
}

export interface InternalRuleDefCharAlt {
  type: typeof InternalRuleType.CHAR_ALT;
  value: number;
}

export interface InternalRuleDefCharRngUpper {
  type: typeof InternalRuleType.CHAR_RNG_UPPER;
  value: number;
}

export interface InternalRuleDefReference {
  type: typeof InternalRuleType.REF;
  value: number;
}

export interface InternalRuleDefAlt {
  type: typeof InternalRuleType.ALT;
}

export interface InternalRuleDefEnd {
  type: typeof InternalRuleType.END;
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

export const internalRuleDefChar = (value: number[]): InternalRuleDefChar => ({
  type: InternalRuleType.CHAR,
  value: [...validateNonEmpty(value)],
});

export const internalRuleDefCharNot = (
  value: number[]
): InternalRuleDefCharNot => ({
  type: InternalRuleType.CHAR_NOT,
  value: [...validateNonEmpty(value)],
});

export const internalRuleDefCharAlt = (
  value: number
): InternalRuleDefCharAlt => ({ type: InternalRuleType.CHAR_ALT, value });

export const internalRuleDefCharRngUpper = (
  value: number
): InternalRuleDefCharRngUpper => ({
  type: InternalRuleType.CHAR_RNG_UPPER,
  value,
});

export const internalRuleDefReference = (
  value: number
): InternalRuleDefReference => ({ type: InternalRuleType.REF, value });

export const internalRuleDefAlt = (): InternalRuleDefAlt => ({
  type: InternalRuleType.ALT,
});

export const internalRuleDefEnd = (): InternalRuleDefEnd => ({
  type: InternalRuleType.END,
});

export const isRuleDefAlt = (rule?: InternalRuleDef): rule is InternalRuleDefAlt =>
  rule?.type === InternalRuleType.ALT;

export const isRuleDefRef = (
  rule?: InternalRuleDef
): rule is InternalRuleDefReference => rule?.type === InternalRuleType.REF;

export const isRuleDefEnd = (rule?: InternalRuleDef): rule is InternalRuleDefEnd =>
  rule?.type === InternalRuleType.END;

export const isRuleDefChar = (rule?: InternalRuleDef): rule is InternalRuleDefChar =>
  rule?.type === InternalRuleType.CHAR;

export const isRuleDefCharNot = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharNot => rule?.type === InternalRuleType.CHAR_NOT;

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharAlt => rule?.type === InternalRuleType.CHAR_ALT;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef
): rule is InternalRuleDefCharRngUpper =>
  rule?.type === InternalRuleType.CHAR_RNG_UPPER;
