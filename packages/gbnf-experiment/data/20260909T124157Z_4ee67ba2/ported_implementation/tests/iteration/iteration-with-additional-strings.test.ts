import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { GBNF, InputParseError } from '../../src/index.ts';
import { label, loadTable, sortRules, transformExpected, type ExpectedRule } from '../helpers.ts';

const FIXTURE = 'iteration_with_additional_strings_test';

describe('iteration with additional strings', () => {
  describe('it raises if encountering grammar with starting string and additional string', () => {
    for (const [grammar, starting, additional] of loadTable(
      FIXTURE,
      'test_it_raises_if_encountering_grammar_with_starting_s_and_additional_s',
    ) as [string, string, string][]) {
      test(label(grammar, starting, additional), () => {
        const state = GBNF(grammar, starting);
        assert.throws(
          () => {
            state.add(additional);
          },
          (err: unknown) => err instanceof InputParseError,
        );
      });
    }
  });

  describe('it parses a grammar with starting and additional', () => {
    for (const [grammar, starting, additional, expected] of loadTable(
      FIXTURE,
      'test_it_parses_a_grammar_with_starting_and_additional',
    ) as [string, string, string, ExpectedRule[]][]) {
      test(label(grammar, starting, additional), () => {
        const state = [...GBNF(grammar, starting).add(additional)];
        assert.deepStrictEqual(
          sortRules(state),
          sortRules(expected.map(transformExpected)),
        );
      });
    }
  });

  describe('it raises a particular error', () => {
    for (const [errorForMostRecentInput] of loadTable(
      FIXTURE,
      'test_it_raises_a_particular_error',
    ) as [boolean][]) {
      test(label(errorForMostRecentInput), () => {
        const grammar = 'root ::= "bar"';
        const state = GBNF(grammar).add('b').add('a');
        const expectedError = new InputParseError('z', 0, 'ba');
        assert.throws(
          () => {
            state.add('z');
          },
          (err: unknown) => {
            assert.ok(err instanceof InputParseError);
            if (errorForMostRecentInput) {
              assert.equal(
                err.errorForMostRecentInput,
                expectedError.errorForMostRecentInput,
              );
            } else {
              assert.equal(String(err), String(expectedError));
            }
            return true;
          },
        );
      });
    }
  });
});
