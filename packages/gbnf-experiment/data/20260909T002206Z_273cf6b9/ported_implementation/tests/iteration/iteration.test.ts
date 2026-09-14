import { describe, expect, test } from 'vitest';
import { GBNF } from '../../src/index.ts';
import fixtures from '../fixtures/iteration.json' with { type: 'json' };
import { label, transformedExpectedDict, type ExpectedRule } from '../helpers.ts';

const cases = fixtures[0].argvalues as [string, ExpectedRule[]][];

describe('iteration', () => {
  test.each(cases.map(([grammar, expected]) => [label(grammar), grammar, expected] as const))(
    'it returns parse state for grammar: %s',
    (_name, grammar, expected) => {
      const state = [...GBNF(grammar)];
      expect(state).toStrictEqual(expected.map(transformedExpectedDict));
    },
  );
});
