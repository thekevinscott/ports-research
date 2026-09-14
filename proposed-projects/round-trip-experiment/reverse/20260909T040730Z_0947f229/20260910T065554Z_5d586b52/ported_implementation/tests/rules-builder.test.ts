// Not part of the generated suite in /workspace/tests. This is the reference
// implementation's own rules-builder case table (copied from
// reference_implementation/tests/fixtures/reference-cases.json), which pins the
// exact internal rule definitions the parser emits — the sharpest check that the
// port matches the reference rather than merely satisfying the public API.
import { describe, test, expect } from 'vitest';
import { RulesBuilder } from '../src/rules-builder/index.js';
import type { InternalRuleDef } from '../src/rules-builder/types.js';
import CASES from './fixtures/reference-cases.json';

interface Expectation {
  symbolIds: [string, number][];
  rules: { type: string; value?: number | number[] }[][];
}

const cases = CASES['rules-builder/rules-builder.test.ts'] as [
  string,
  string,
  Expectation,
][];

// `{ type: ALT }` has no `value` key at all in the reference expectations.
const asPlain = (ruleDef: InternalRuleDef) =>
  ruleDef.value === undefined
    ? { type: ruleDef.type as string }
    : { type: ruleDef.type as string, value: ruleDef.value };

describe('RulesBuilder', () => {
  test.for(cases)('It parses a grammar: %s', ([, grammar, expectation]) => {
    const parsedGrammar = new RulesBuilder(grammar);
    expect(parsedGrammar.rules.map((rule) => (rule ?? []).map(asPlain))).toEqual(
      expectation.rules,
    );
    expect([...parsedGrammar.symbolIds].map((entry) => [...entry])).toEqual(
      expectation.symbolIds.map((entry) => [...entry]),
    );
  });
});
