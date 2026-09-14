import {
  type Range,
  type ResolvedRule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from '../src/index.js';

/**
 * The shape the test tables use to describe an expected rule, mirroring the
 * dictionaries used by the generated Python suite.
 */
export type ExpectedRule =
  | { type: 'char'; value: (number | Range)[] }
  | { type: 'char_exclude'; value: (number | Range)[] }
  | { type: 'end' };

export const toRule = (expected: ExpectedRule): ResolvedRule => {
  switch (expected.type) {
    case 'char':
      return new RuleChar(expected.value);
    case 'char_exclude':
      return new RuleCharExclude(expected.value);
    case 'end':
      return new RuleEnd();
    default:
      throw new Error(
        `Unknown type found in expectation array: ${JSON.stringify(expected)}`,
      );
  }
};

export const toRules = (expected: ExpectedRule[]): ResolvedRule[] => expected.map(toRule);

/**
 * Order-insensitive comparison helper, matching the Python suite's
 * `sorted(rules, key=lambda r: json.dumps(r.__dict__))`.
 */
export const sortRules = <T>(rules: Iterable<T>): T[] =>
  [...rules].sort((a, b) => {
    const left = JSON.stringify(a);
    const right = JSON.stringify(b);
    return left < right ? -1 : left > right ? 1 : 0;
  });

/** `ord('a')` — spelled out so the generated tables read like the originals. */
export const ord = (char: string): number => char.codePointAt(0) as number;
