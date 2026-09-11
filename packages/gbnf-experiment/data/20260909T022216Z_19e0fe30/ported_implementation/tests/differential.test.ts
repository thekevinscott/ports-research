import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { GBNF, type ResolvedRule } from '../src/index.js';

/**
 * Differential test against the python reference implementation.
 *
 * Every grammar test case is replayed one character at a time, and the set of
 * rules the parser accepts next is compared, after every character, against a
 * trace recorded from reference_implementation/ (see
 * tools/record-reference-trace.py).
 *
 * Rule sets are compared sorted: the reference yields rules in an order derived
 * from python `set` iteration over graph nodes, which is keyed on object
 * identity and so varies between runs. The accepted rule set is the contract;
 * its order is not.
 */
const here = dirname(fileURLToPath(import.meta.url));
const grammarsDir = join(here, 'iteration', 'grammars');

const referenceTrace = JSON.parse(
  readFileSync(join(here, 'fixtures', 'reference-trace.json'), 'utf8'),
) as Record<string, string[][][]>;

const grammarKeys = readdirSync(grammarsDir)
  .filter((file) => file.endsWith('.gbnf'))
  .map((file) => file.replace(/\.gbnf$/, ''))
  .sort();

const snapshot = (rules: Iterable<ResolvedRule>): string[] =>
  [...rules]
    .map((rule) => {
      const { type, value } = rule.toJSON();
      // keys sorted, to match the python recorder's serialization
      return value === undefined
        ? JSON.stringify({ type })
        : JSON.stringify({ type, value });
    })
    .sort();

describe('differential against the python reference', () => {
  it.each(grammarKeys)('matches the reference trace for %s', (key) => {
    const grammar = readFileSync(join(grammarsDir, `${key}.gbnf`), 'utf8');
    const cases = JSON.parse(
      readFileSync(join(grammarsDir, `${key}.json`), 'utf8'),
    ) as string[];

    const expectedTraces = referenceTrace[key];
    expect(expectedTraces).toBeDefined();

    const traces = cases.map((testCase) => {
      let state = GBNF(grammar);
      const trace: string[][] = [snapshot(state)];
      for (const char of testCase) {
        state = state.add(char);
        trace.push(snapshot(state));
      }
      return trace;
    });

    expect(traces).toEqual(expectedTraces);
  });
});
