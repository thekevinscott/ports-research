import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, it } from 'vitest';
import { GBNF } from '../../src/index.js';

const grammarsDir = join(dirname(fileURLToPath(import.meta.url)), 'grammars');

const loadCases = (): [key: string, testCase: string, grammar: string][] => {
  const cases: [string, string, string][] = [];
  for (const file of readdirSync(grammarsDir).sort()) {
    if (!file.endsWith('.gbnf')) {
      continue;
    }
    const key = file.slice(0, -'.gbnf'.length);
    const grammar = readFileSync(join(grammarsDir, file), 'utf-8');
    const testCases: string[] = JSON.parse(
      readFileSync(join(grammarsDir, `${key}.json`), 'utf-8'),
    );
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
  it.each(loadCases())('parses the known valid grammar %s with %j', (_key, testCase, grammar) => {
    let state = GBNF(grammar);
    for (const char of testCase) {
      state = state.add(char);
    }
  });
});
