// Ported from the generated Python suite at tests/python.
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { GBNF } from '../../src/index.js';

const grammarsDir = join(dirname(fileURLToPath(import.meta.url)), 'grammars');

const loadCases = (): [key: string, testCase: string, grammar: string][] => {
  const cases: [string, string, string][] = [];
  const grammarFiles = readdirSync(grammarsDir)
    .filter(file => file.endsWith('.gbnf'))
    .sort();
  for (const file of grammarFiles) {
    const key = file.slice(0, -'.gbnf'.length);
    const grammar = readFileSync(join(grammarsDir, file), 'utf-8');
    const testCases = JSON.parse(
      readFileSync(join(grammarsDir, `${key}.json`), 'utf-8'),
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
  it.each(loadCases())('parses a known valid grammar: %s (case %#)', (_key, testCase, grammar) => {
    let state = GBNF(grammar);
    // Iterate by code point, matching how the grammar walks its input.
    for (const char of testCase) {
      state = state.add(char);
    }
    expect(state).toBeTruthy();
  });
});
