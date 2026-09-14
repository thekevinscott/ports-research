import { describe, expect, test } from 'vitest';
import { GBNF, InputParseError } from '../../src/index.ts';
import fixtures from '../fixtures/validate-input.json' with { type: 'json' };
import { label } from '../helpers.ts';

const validInputs = fixtures[0].argvalues as [string, string][];
const invalidInputs = fixtures[1].argvalues as [string, string, number][];

describe('validate_input', () => {
  test.each(validInputs.map(([grammar, input]) => [label(grammar, input), grammar, input] as const))(
    'it parses a grammar: %s',
    (_name, grammar, input) => {
      const graph = GBNF(grammar, input);
      expect(Boolean(graph)).toBe(true);
    },
  );

  test.each(
    invalidInputs.map(([grammar, inputText, errorPos]) =>
      [label(grammar, inputText, errorPos), grammar, inputText, errorPos] as const),
  )(
    'it reports an error for an invalid input: %s',
    (_name, grammar, inputText, errorPos) => {
      const graph = GBNF(grammar);
      const expected = new InputParseError(inputText, errorPos);
      let thrown: unknown;
      try {
        graph.add(inputText);
      } catch (err) {
        thrown = err;
      }
      expect(thrown).toBeInstanceOf(InputParseError);
      expect(String(thrown)).toBe(String(expected));
    },
  );
});
