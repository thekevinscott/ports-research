import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { GBNF, GrammarParseError } from '../../src/index.ts';
import { label, loadTable } from '../helpers.ts';

describe('validate grammar', () => {
  describe('it parses a grammar', () => {
    for (const [grammar] of loadTable('validate_grammar_test', 'test_it_parses_a_grammar') as [
      string,
    ][]) {
      test(label(grammar), () => {
        GBNF(grammar);
      });
    }
  });

  describe('it reports an error for an invalid grammar', () => {
    for (const [grammar, errorPos, errorReason] of loadTable(
      'validate_grammar_test',
      'test_it_reports_an_error_for_an_invalid_grammar',
    ) as [string, number, string][]) {
      test(label(grammar, errorPos, errorReason), () => {
        const expected = new GrammarParseError(grammar, errorPos, errorReason);
        assert.throws(
          () => {
            GBNF(grammar);
          },
          (err: unknown) => {
            assert.ok(err instanceof GrammarParseError);
            assert.equal(String(err), String(expected));
            return true;
          },
        );
      });
    }
  });
});
