import { describe, expect, it } from 'vitest';

import { GBNF, InputParseError } from '../../src/index.js';
import fixtures from '../fixtures/validate_input_test.json';
import { label, type Fixtures } from '../helpers.js';

const cases = fixtures as unknown as Fixtures;

describe('validate_input', () => {
  it.each(cases.test_it_parses_a_grammar.argvalues.map((v) => [label(v), v]))(
    'it parses a grammar: %s',
    (_name, values) => {
      const [grammar, input] = values as [string, string];
      const graph = GBNF(grammar, input);
      expect(Boolean(graph)).toBe(true);
    },
  );

  it.each(
    cases.test_it_reports_an_error_for_an_invalid_input.argvalues.map((v) => [
      label(v),
      v,
    ]),
  )('it reports an error for an invalid input: %s', (_name, values) => {
    const [grammar, inputText, errorPos] = values as [string, string, number];
    const graph = GBNF(grammar);
    const expected = new InputParseError(inputText, errorPos);
    let thrown: unknown;
    try {
      graph.add(inputText);
    } catch (err) {
      thrown = err;
    }
    expect(thrown).toBeInstanceOf(InputParseError);
    expect((thrown as InputParseError).equals(expected)).toBe(true);
  });
});
