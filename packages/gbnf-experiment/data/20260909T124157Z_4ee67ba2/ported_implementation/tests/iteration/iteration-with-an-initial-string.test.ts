import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { GBNF } from '../../src/index.ts';
import { label, loadTable, sortRules, transformExpected, type ExpectedRule } from '../helpers.ts';

describe('iteration with an initial string', () => {
  describe('it returns parse state for grammar and initial string', () => {
    for (const [grammar, inputString, expected] of loadTable(
      'iteration_with_an_initial_string_test',
      'test_it_returns_parse_state_for_grammar_and_initial_string',
    ) as [string, string, ExpectedRule[]][]) {
      test(label(grammar, inputString), () => {
        const state = [...GBNF(grammar).add(inputString)];
        assert.deepStrictEqual(
          sortRules(state),
          sortRules(expected.map(transformExpected)),
        );
      });
    }
  });
});
