import { describe, expect, test } from 'vitest';
import { GBNF } from '../../src/index.ts';
import fixtures from '../fixtures/iteration-with-an-initial-string.json' with { type: 'json' };
import { label, sortRules, transformedExpectedDict, type ExpectedRule } from '../helpers.ts';

const cases = fixtures[0].argvalues as [string, string, ExpectedRule[]][];

describe('iteration', () => {
  test.each(
    cases.map(([grammar, inputString, expected]) =>
      [label(grammar, inputString), grammar, inputString, expected] as const),
  )(
    'it returns parse state for grammar and initial string: %s',
    (_name, grammar, inputString, expected) => {
      const state = GBNF(grammar).add(inputString);
      expect(sortRules(state)).toStrictEqual(sortRules(expected.map(transformedExpectedDict)));
    },
  );
});
