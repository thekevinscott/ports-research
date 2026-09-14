import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { GBNF } from '../../src/index.js';

const grammarsDir = join(dirname(fileURLToPath(import.meta.url)), 'grammars');

const loadCases = (): [string, string, string][] => {
  const cases: [string, string, string][] = [];
  const grammarFiles = readdirSync(grammarsDir)
    .filter((file) => file.endsWith('.gbnf'))
    .sort();
  for (const file of grammarFiles) {
    const key = file.replace(/\.gbnf$/, '');
    const grammar = readFileSync(join(grammarsDir, file), 'utf8');
    const testCases = JSON.parse(
      readFileSync(join(grammarsDir, `${key}.json`), 'utf8'),
    ) as string[];
    for (const testCase of testCases) {
      cases.push([key, testCase, grammar]);
    }
  }
  if (cases.length === 0) {
    throw new Error('No grammar test cases found');
  }
  return cases;
};

describe('grammars', () => {
  it.each(loadCases().map((c, idx) => [`${c[0]} #${idx}`, c]))(
    'it parses a known valid grammar: %s',
    (_name, values) => {
      const [, testCase, grammar] = values as [string, string, string];
      let state = GBNF(grammar);
      for (const char of testCase) {
        state = state.add(char);
      }
      expect(state).toBeDefined();
    },
  );
});
