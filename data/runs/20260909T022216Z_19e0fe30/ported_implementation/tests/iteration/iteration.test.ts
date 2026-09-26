import { describe, expect, it } from 'vitest';

import { GBNF } from '../../src/index.js';
import fixtures from '../fixtures/iteration_test.json';
import {
  expectedRules,
  label,
  toPlain,
  type ExpectedRule,
  type Fixtures,
} from '../helpers.js';

const cases = fixtures as unknown as Fixtures;

describe('iteration', () => {
  it.each(
    cases.test_it_returns_parse_state_for_grammar.argvalues.map((v) => [
      label([v[0]]),
      v,
    ]),
  )('it returns parse state for grammar: %s', (_name, values) => {
    const [grammar, expected] = values as [string, ExpectedRule[]];
    const state = [...GBNF(grammar)];
    expect(toPlain(state)).toEqual(toPlain(expectedRules(expected)));
  });
});
