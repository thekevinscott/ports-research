import { describe, expect, it } from 'vitest';

import { GBNF, InputParseError } from '../../src/index.js';
import fixtures from '../fixtures/iteration_with_additional_strings_test.json';
import {
  expectedRules,
  label,
  sortedPlain,
  type ExpectedRule,
  type Fixtures,
} from '../helpers.js';

const cases = fixtures as unknown as Fixtures;

describe('iteration', () => {
  it.each(
    cases.test_it_raises_if_encountering_grammar_with_starting_s_and_additional_s.argvalues.map(
      (v) => [label(v), v],
    ),
  )(
    'it raises if encountering grammar with starting s and additional s: %s',
    (_name, values) => {
      const [grammar, starting, additional] = values as [
        string,
        string,
        string,
      ];
      const state = GBNF(grammar, starting);
      expect(() => state.add(additional)).toThrow(InputParseError);
    },
  );

  it.each(
    cases.test_it_parses_a_grammar_with_starting_and_additional.argvalues.map(
      (v) => [label([v[0], v[1], v[2]]), v],
    ),
  )(
    'it parses a grammar with starting and additional: %s',
    (_name, values) => {
      const [grammar, starting, additional, expected] = values as [
        string,
        string,
        string,
        ExpectedRule[],
      ];
      const state = GBNF(grammar, starting).add(additional);
      expect(sortedPlain(state)).toEqual(sortedPlain(expectedRules(expected)));
    },
  );

  it.each(
    cases.test_it_raises_a_particular_error.argvalues.map((v) => [
      label(v),
      v,
    ]),
  )('it raises a particular error: %s', (_name, values) => {
    const [errorForMostRecentInput] = values as [boolean];
    const grammar = 'root ::= "bar"';
    let state = GBNF(grammar);
    state = state.add('b');
    state = state.add('a');

    let thrown: unknown;
    try {
      state.add('z');
    } catch (err) {
      thrown = err;
    }
    expect(thrown).toBeInstanceOf(InputParseError);
    const err = thrown as InputParseError;
    const expectedError = new InputParseError('z', 0, 'ba');
    if (errorForMostRecentInput) {
      expect(err.errorForMostRecentInput).toBe(
        expectedError.errorForMostRecentInput,
      );
    } else {
      expect(String(err)).toBe(String(expectedError));
    }
  });
});
