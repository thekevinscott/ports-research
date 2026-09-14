import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { GBNF } from '../../src/index.ts';
import { label, loadTable, transformExpected, type ExpectedRule } from '../helpers.ts';

describe('iteration', () => {
  describe('it returns parse state for grammar', () => {
    for (const [grammar, expected] of loadTable(
      'iteration_test',
      'test_it_returns_parse_state_for_grammar',
    ) as [string, ExpectedRule[]][]) {
      test(label(grammar), () => {
        const state = [...GBNF(grammar)];
        assert.deepStrictEqual(state, expected.map(transformExpected));
      });
    }
  });
});
