import { describe, expect, test } from 'vitest';

import fixtures from './fixtures/reference_fixtures.json' with { type: 'json' };

import {
  buildRuleStack,
  GBNF,
  GrammarParseError,
  InputParseError,
  RulesBuilder,
  type InternalRuleDef,
  type ParseState,
  type ResolvedRule,
} from '../index.ts';

interface SerializedRule {
  type: string;
  value?: unknown;
}

interface StepFixture {
  rules?: SerializedRule[];
  size?: number;
  error?: string;
  message?: string;
}

interface GrammarFixture {
  grammar: string;
  rules?: SerializedRule[][];
  symbolIds?: Record<string, number>;
  stackedRules?: SerializedRule[][][];
  rulesError?: { error: string; message: string };
  initialRules?: SerializedRule[];
  size?: number;
  initialError?: { error: string; message: string };
  inputs?: (StepFixture & { input: string })[];
  sequences?: { chunks: string[]; steps: (StepFixture & { chunk?: string })[] }[];
}

const serialize = (rule: InternalRuleDef | ResolvedRule): SerializedRule =>
  'value' in rule ? { type: rule.type, value: rule.value } : { type: rule.type };

/**
 * The set of rules a parse state can accept next.
 *
 * The reference implementation collects the nodes a rule reference points at in
 * a Python `set`, which has no defined iteration order, so the order rules come
 * back in is not meaningful (in the port, backed by a JS `Set`, it is stable).
 * Parity is therefore asserted on the set of rules, not on their order.
 */
const rulesOf = (state: ParseState): string[] =>
  Array.from(state)
    .map((rule) => JSON.stringify(serialize(rule)))
    .sort();

const expectedRules = (rules: SerializedRule[] = []): string[] =>
  rules.map((rule) => JSON.stringify(rule)).sort();

/**
 * The reference implementation indexes past the end of the grammar string in a
 * handful of malformed-input cases, which raises a bare `IndexError` (or a
 * `KeyError` for a grammar with no `root` rule). Where the reference raises one
 * of its own error types we assert the message matches exactly; otherwise we
 * only assert that the port throws too.
 */
const REFERENCE_ERRORS = new Set(['GrammarParseError', 'InputParseError']);

const expectError = (fn: () => unknown, expected: { error: string; message: string }): void => {
  let thrown: unknown;
  try {
    fn();
  } catch (err) {
    thrown = err;
  }
  expect(thrown, `expected ${expected.error} to be thrown`).toBeInstanceOf(Error);
  if (REFERENCE_ERRORS.has(expected.error)) {
    expect((thrown as Error).constructor.name).toBe(expected.error);
    expect((thrown as Error).message).toBe(expected.message);
  }
};

const cases = fixtures as unknown as {
  grammars: GrammarFixture[];
  invalidGrammars: GrammarFixture[];
};

describe('parity with the reference implementation', () => {
  describe.each(cases.grammars.map((fixture, idx) => [idx, fixture] as const))(
    'grammar %i',
    (_idx, fixture) => {
      test('builds the same rules and symbol ids', () => {
        const rulesBuilder = new RulesBuilder(fixture.grammar);
        expect(rulesBuilder.rules.map((rules) => rules.map(serialize))).toEqual(fixture.rules);
        expect(Object.fromEntries(rulesBuilder.symbolIds.entries())).toEqual(fixture.symbolIds);
      });

      test('builds the same rule stacks', () => {
        const rulesBuilder = new RulesBuilder(fixture.grammar);
        expect(
          rulesBuilder.rules.map((rules) =>
            buildRuleStack(rules).map((path) => path.map(serialize)),
          ),
        ).toEqual(fixture.stackedRules);
      });

      test('returns the same initial rules', () => {
        const state = GBNF(fixture.grammar);
        expect(rulesOf(state)).toEqual(expectedRules(fixture.initialRules));
        expect(state.size).toBe(fixture.size);
      });

      test('parses the same inputs', () => {
        for (const input of fixture.inputs ?? []) {
          if (input.error) {
            expectError(
              () => GBNF(fixture.grammar, input.input),
              { error: input.error, message: input.message as string },
            );
          } else {
            const state = GBNF(fixture.grammar, input.input);
            expect(rulesOf(state), `input: ${JSON.stringify(input.input)}`).toEqual(
              expectedRules(input.rules),
            );
            expect(state.size, `input: ${JSON.stringify(input.input)}`).toBe(input.size);
          }
        }
      });

      test('parses the same input sequences', () => {
        for (const sequence of fixture.sequences ?? []) {
          let state: ParseState | undefined;
          for (let i = 0; i < sequence.steps.length; i++) {
            const step = sequence.steps[i];
            const chunk = sequence.chunks[i];
            if (step.error) {
              expectError(
                () => (state ? state.add(chunk) : GBNF(fixture.grammar, chunk)),
                { error: step.error, message: step.message as string },
              );
              break;
            }
            state = state ? state.add(chunk) : GBNF(fixture.grammar).add(chunk);
            expect(rulesOf(state), `chunks: ${JSON.stringify(sequence.chunks)}`).toEqual(
              expectedRules(step.rules),
            );
            expect(state.size).toBe(step.size);
          }
        }
      });
    },
  );

  describe.each(cases.invalidGrammars.map((fixture, idx) => [idx, fixture] as const))(
    'invalid grammar %i',
    (_idx, fixture) => {
      const expected = fixture.rulesError ?? fixture.initialError;

      test('fails the same way', () => {
        if (expected === undefined) {
          // The reference accepts this grammar; so should the port.
          expect(() => GBNF(fixture.grammar)).not.toThrow();
          return;
        }
        expectError(() => GBNF(fixture.grammar), expected);
      });
    },
  );
});

describe('error types', () => {
  test('GrammarParseError carries the grammar, position and reason', () => {
    expect(() => GBNF('root ::= foo')).toThrowError(GrammarParseError);
    try {
      GBNF('root ::= foo');
    } catch (err) {
      const error = err as GrammarParseError;
      expect(error.reason).toBe('Undefined rule identifier "foo"');
      expect(error.pos).toBe(9);
      expect(error.grammar).toBe('root ::= foo');
    }
  });

  test('InputParseError reports the position of the failing input', () => {
    expect(() => GBNF('root ::= "foo"', 'fob')).toThrowError(InputParseError);
    try {
      GBNF('root ::= "foo"', 'fob');
    } catch (err) {
      const error = err as InputParseError;
      expect(error.pos).toBe(2);
      expect(error.src).toBe('fob');
    }
  });
});
