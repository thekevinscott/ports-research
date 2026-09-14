import { describe, expect, it } from 'vitest';

import { GBNF, GrammarParseError } from '../../src/index.js';
import fixtures from '../fixtures/validate_grammar_test.json';
import { label, type Fixtures } from '../helpers.js';

const cases = fixtures as unknown as Fixtures;

describe('validate_grammar', () => {
  it.each(cases.test_it_parses_a_grammar.argvalues.map((v) => [label(v), v]))(
    'it parses a grammar: %s',
    (_name, values) => {
      const [grammar] = values as [string];
      expect(() => GBNF(grammar)).not.toThrow();
    },
  );

  it.each(
    cases.test_it_reports_an_error_for_an_invalid_grammar.argvalues.map((v) => [
      label(v),
      v,
    ]),
  )('it reports an error for an invalid grammar: %s', (_name, values) => {
    const [grammar, errorPos, errorReason] = values as [string, number, string];
    const expected = new GrammarParseError(grammar, errorPos, errorReason);
    let thrown: unknown;
    try {
      GBNF(grammar);
    } catch (err) {
      thrown = err;
    }
    expect(thrown).toBeInstanceOf(GrammarParseError);
    expect((thrown as GrammarParseError).equals(expected)).toBe(true);
  });
});
