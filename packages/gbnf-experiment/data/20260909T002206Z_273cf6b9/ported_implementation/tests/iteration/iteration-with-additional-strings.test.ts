import { describe, expect, test } from 'vitest';
import { GBNF, InputParseError } from '../../src/index.ts';
import fixtures from '../fixtures/iteration-with-additional-strings.json' with { type: 'json' };
import { label, sortRules, transformedExpectedDict, type ExpectedRule } from '../helpers.ts';

const raisingCases = fixtures[0].argvalues as [string, string, string][];
const parsingCases = fixtures[1].argvalues as [string, string, string, ExpectedRule[]][];
const errorForMostRecentInputCases = fixtures[2].argvalues as boolean[];

describe('iteration', () => {
  test.each(
    raisingCases.map(([grammar, starting, additional]) =>
      [label(grammar, starting, additional), grammar, starting, additional] as const),
  )(
    'it raises if encountering grammar with starting %s',
    (_name, grammar, starting, additional) => {
      const state = GBNF(grammar, starting);
      expect(() => state.add(additional)).toThrow(InputParseError);
    },
  );

  test.each(
    parsingCases.map(([grammar, starting, additional, expected]) =>
      [label(grammar, starting, additional), grammar, starting, additional, expected] as const),
  )(
    'it parses a grammar with starting and additional: %s',
    (_name, grammar, starting, additional, expected) => {
      const state = GBNF(grammar, starting).add(additional);
      expect(sortRules(state)).toStrictEqual(sortRules(expected.map(transformedExpectedDict)));
    },
  );

  test.each(errorForMostRecentInputCases)(
    'it raises a particular error (error_for_most_recent_input: %s)',
    errorForMostRecentInput => {
      const grammar = 'root ::= "bar"';
      let state = GBNF(grammar);
      state = state.add('b');
      state = state.add('a');
      let err: unknown;
      try {
        state.add('z');
      } catch (thrown) {
        err = thrown;
      }
      expect(err).toBeInstanceOf(InputParseError);
      const expectedError = new InputParseError('z', 0, 'ba');
      if (errorForMostRecentInput) {
        expect((err as InputParseError).errorForMostRecentInput)
          .toBe(expectedError.errorForMostRecentInput);
      } else {
        expect(String(err)).toBe(String(expectedError));
      }
    },
  );
});
