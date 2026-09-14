import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { GBNF, InputParseError } from '../../src/index.ts';
import { label, loadTable } from '../helpers.ts';

describe('validate input', () => {
  describe('it parses a grammar', () => {
    for (const [grammar, input] of loadTable(
      'validate_input_test',
      'test_it_parses_a_grammar',
    ) as [string, string][]) {
      test(label(grammar, input), () => {
        const graph = GBNF(grammar, input);
        assert.equal(Boolean(graph), true);
      });
    }
  });

  describe('it reports an error for an invalid input', () => {
    for (const [grammar, inputText, errorPos] of loadTable(
      'validate_input_test',
      'test_it_reports_an_error_for_an_invalid_input',
    ) as [string, string, number][]) {
      test(label(grammar, inputText, errorPos), () => {
        const graph = GBNF(grammar);
        const expected = new InputParseError(inputText, errorPos);
        assert.throws(
          () => {
            graph.add(inputText);
          },
          (err: unknown) => {
            assert.ok(err instanceof InputParseError);
            assert.equal(String(err), String(expected));
            return true;
          },
        );
      });
    }
  });
});
