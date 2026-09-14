export enum InternalRuleType {
  CHAR = 'char',
  CHAR_ALT = 'char_alt',
  ALT = 'alt',
  CHAR_NOT = 'char_not',
  CHAR_RNG_UPPER = 'char_rng_upper',
  REF = 'ref',
  END = 'end',
}

export abstract class InternalBase {
  abstract readonly type: InternalRuleType;
}

export abstract class InternalBaseWithInt extends InternalBase {
  value: number;

  constructor(value: number) {
    super();
    this.value = value;
  }
}

export abstract class InternalBaseWithListOfInts extends InternalBase {
  value: number[];

  constructor(value: number[]) {
    super();
    // the incoming list is copied so later mutations of the source do not leak in.
    this.value = value.slice();
  }
}

export class InternalRuleDefChar extends InternalBaseWithListOfInts {
  readonly type = InternalRuleType.CHAR;
}

export class InternalRuleDefCharNot extends InternalBaseWithListOfInts {
  readonly type = InternalRuleType.CHAR_NOT;
}

export class InternalRuleDefCharAlt extends InternalBaseWithInt {
  readonly type = InternalRuleType.CHAR_ALT;
}

export class InternalRuleDefCharRngUpper extends InternalBaseWithInt {
  readonly type = InternalRuleType.CHAR_RNG_UPPER;
}

export class InternalRuleDefReference extends InternalBaseWithInt {
  readonly type = InternalRuleType.REF;
}

export class InternalRuleDefAlt extends InternalBase {
  readonly type = InternalRuleType.ALT;
}

export class InternalRuleDefEnd extends InternalBase {
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
  rule?: InternalRuleDef,
): rule is InternalRuleDefAlt => rule instanceof InternalRuleDefAlt;

export const isRuleDefRef = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefReference => rule instanceof InternalRuleDefReference;

export const isRuleDefEnd = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefEnd => rule instanceof InternalRuleDefEnd;

export const isRuleDefChar = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefChar => rule instanceof InternalRuleDefChar;

export const isRuleDefCharNot = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharNot => rule instanceof InternalRuleDefCharNot;

export const isRuleDefCharAlt = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharAlt => rule instanceof InternalRuleDefCharAlt;

export const isRuleDefCharRngUpper = (
  rule?: InternalRuleDef,
): rule is InternalRuleDefCharRngUpper =>
  rule instanceof InternalRuleDefCharRngUpper;
