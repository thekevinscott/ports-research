import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type ResolvedRule,
} from '../src/index.js';

export type ExpectedRule =
  | { type: 'char'; value: (number | Range)[] }
  | { type: 'char_exclude'; value: (number | Range)[] }
  | { type: 'end' };

/** Mirrors the `transformed_expected_dict` helper used throughout the Python suite. */
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

/**
 * Sorts rules by their serialized form, matching the Python suite's
 * `sorted(rules, key=lambda r: json.dumps(r.__dict__))`.
 */
export const sortRules = (rules: ResolvedRule[]): ResolvedRule[] =>
  [...rules].sort((a, b) => {
    const keyA = JSON.stringify(a.toDict());
    const keyB = JSON.stringify(b.toDict());
    if (keyA < keyB) {
      return -1;
    }
    return keyA > keyB ? 1 : 0;
  });

/** Runs `fn`, asserting it throws an instance of `ctor`, and returns the thrown error. */
export const captureError = <T extends Error>(
  ctor: new (...args: never[]) => T,
  fn: () => unknown,
): T => {
  try {
    fn();
  } catch (err) {
    if (err instanceof ctor) {
      return err;
    }
    throw err;
  }
  throw new Error(`Expected the call to throw ${ctor.name}, but it did not throw`);
};
