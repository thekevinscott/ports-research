import { describe, expect, it } from 'vitest';

import { GBNF } from '../../src/index.js';
import fixtures from '../fixtures/iteration_with_an_initial_string_test.json';
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
    cases.test_it_returns_parse_state_for_grammar_and_initial_string.argvalues.map(
      (v) => [label([v[0], v[1]]), v],
    ),
  )(
    'it returns parse state for grammar and initial string: %s',
    (_name, values) => {
      const [grammar, inputString, expected] = values as [
        string,
        string,
        ExpectedRule[],
      ];
      const state = GBNF(grammar).add(inputString);
      expect(sortedPlain(state)).toEqual(
        sortedPlain(expectedRules(expected)),
      );
    },
  );
});
