import { describe, expect, test } from 'vitest';
import { GBNF, GrammarParseError } from '../../src/index.ts';
import fixtures from '../fixtures/validate-grammar.json' with { type: 'json' };
import { label } from '../helpers.ts';

const validGrammars = fixtures[0].argvalues as string[];
const invalidGrammars = fixtures[1].argvalues as [string, number, string][];

describe('validate_grammar', () => {
  test.each(validGrammars.map(grammar => [label(grammar), grammar] as const))(
    'it parses a grammar: %s',
    (_name, grammar) => {
      expect(() => GBNF(grammar)).not.toThrow();
    },
  );

  test.each(
    invalidGrammars.map(([grammar, errorPos, errorReason]) =>
      [label(grammar, errorPos, errorReason), grammar, errorPos, errorReason] as const),
  )(
    'it reports an error for an invalid grammar: %s',
    (_name, grammar, errorPos, errorReason) => {
      const expected = new GrammarParseError(grammar, errorPos, errorReason);
      let thrown: unknown;
      try {
        GBNF(grammar);
      } catch (err) {
        thrown = err;
      }
      expect(thrown).toBeInstanceOf(GrammarParseError);
      expect(String(thrown)).toBe(String(expected));
    },
  );
});
