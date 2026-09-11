export abstract class InternalBase {
  abstract get type(): string;

  equals(other: unknown): boolean {
    return other instanceof InternalBase && other.constructor === this.constructor;
  }

  toString(): string {
    return `${this.type}()`;
  }
}

export abstract class InternalBaseWithValue<T> extends InternalBase {
  value: T;

  constructor(value: T) {
    super();
    this.value = value;
  }

  override equals(other: unknown): boolean {
    return (
      other instanceof InternalBaseWithValue &&
      other.constructor === this.constructor &&
      JSON.stringify(this.value) === JSON.stringify(other.value)
    );
  }

  override toString(): string {
    return `${this.type}(value=${JSON.stringify(this.value)})`;
  }
}

export abstract class InternalBaseWithInt extends InternalBaseWithValue<number> {}

export abstract class InternalBaseWithListOfInts extends InternalBaseWithValue<number[]> {
  constructor(value: number[] = []) {
    super([...value]);
  }
}

export class InternalRuleDefWithNumericValue extends InternalBaseWithInt {
  get type(): 'InternalRuleDefWithNumericValue' {
    return 'InternalRuleDefWithNumericValue';
  }
}

export class InternalRuleDefChar extends InternalBaseWithListOfInts {
  get type(): 'InternalRuleDefChar' {
    return 'InternalRuleDefChar';
  }
}

export class InternalRuleDefCharAlt extends InternalBaseWithInt {
  get type(): 'InternalRuleDefCharAlt' {
    return 'InternalRuleDefCharAlt';
  }
}

export class InternalRuleDefAlt extends InternalBase {
  get type(): 'InternalRuleDefAlt' {
    return 'InternalRuleDefAlt';
  }
}

export class InternalRuleDefCharNot extends InternalBaseWithListOfInts {
  get type(): 'InternalRuleDefCharNot' {
    return 'InternalRuleDefCharNot';
  }
}

export class InternalRuleDefCharRngUpper extends InternalBaseWithInt {
  get type(): 'InternalRuleDefCharRngUpper' {
    return 'InternalRuleDefCharRngUpper';
  }
}

export class InternalRuleDefReference extends InternalBaseWithInt {
  get type(): 'InternalRuleDefReference' {
    return 'InternalRuleDefReference';
  }
}

export class InternalRuleDefEnd extends InternalBase {
  get type(): 'InternalRuleDefEnd' {
    return 'InternalRuleDefEnd';
  }
}

export class InternalRuleDefWithoutValue extends InternalBase {
  get type(): 'InternalRuleDefWithoutValue' {
    return 'InternalRuleDefWithoutValue';
  }
}

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

export const isRuleDefCharRngUpper = (
  rule: unknown,
): rule is InternalRuleDefCharRngUpper => rule instanceof InternalRuleDefCharRngUpper;
