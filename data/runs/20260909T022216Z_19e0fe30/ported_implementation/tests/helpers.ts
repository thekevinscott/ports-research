import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type ResolvedRule,
} from '../src/index.js';

export interface Fixture {
  test: string;
  argnames: string[];
  argvalues: unknown[][];
}

export type Fixtures = Record<string, Fixture>;

export interface ExpectedRule {
  type: string;
  value?: (number | Range)[];
}

/**
 * Mirrors `transformed_expected_dict` from the python suite.
 */
export const transformExpectedRule = (e: ExpectedRule): ResolvedRule => {
  if (e.type === 'char') {
    return new RuleChar(e.value ?? []);
  }
  if (e.type === 'char_exclude') {
    return new RuleCharExclude(e.value ?? []);
  }
  if (e.type === 'end') {
    return new RuleEnd();
  }
  throw new Error(`Unknown type found in expectation array: ${e.type}`);
};

export const toPlain = (rules: Iterable<ResolvedRule>): unknown[] =>
  [...rules].map((rule) => rule.toJSON());

/**
 * Mirrors `sorted(state, key=lambda r: json.dumps(r.__dict__))` from the
 * python suite: both sides are sorted with the same key before comparison.
 */
export const sortedPlain = (rules: Iterable<ResolvedRule>): unknown[] =>
  toPlain(rules).sort((a, b) => {
    const keyA = JSON.stringify(a);
    const keyB = JSON.stringify(b);
    return keyA < keyB ? -1 : keyA > keyB ? 1 : 0;
  });

export const expectedRules = (expected: ExpectedRule[]): ResolvedRule[] =>
  expected.map(transformExpectedRule);

export const label = (values: unknown[]): string =>
  values.map((value) => JSON.stringify(value)).join(' | ');
