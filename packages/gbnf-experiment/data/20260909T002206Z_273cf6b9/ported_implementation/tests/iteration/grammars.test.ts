import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, test } from 'vitest';
import { GBNF } from '../../src/index.ts';

const GRAMMARS_DIR = fileURLToPath(new URL('./grammars', import.meta.url));

const loadCases = (): [string, string, string][] => {
  const cases: [string, string, string][] = [];
  for (const fileName of readdirSync(GRAMMARS_DIR).sort()) {
    if (!fileName.endsWith('.gbnf')) {
      continue;
    }
    const key = fileName.slice(0, -'.gbnf'.length);
    const grammar = readFileSync(`${GRAMMARS_DIR}/${fileName}`, 'utf8');
    const testCases = JSON.parse(
      readFileSync(`${GRAMMARS_DIR}/${key}.json`, 'utf8'),
    ) as string[];
    for (const testCase of testCases) {
      cases.push([key, testCase, grammar]);
    }
  }
  if (!cases.length) {
    throw new Error('No grammar test cases found');
  }
  return cases;
};

describe('grammars', () => {
  test.each(loadCases().map(([key, testCase, grammar], idx) =>
    [`${key}[${idx}]: ${JSON.stringify(testCase)}`, testCase, grammar] as const))(
    'it parses a known valid grammar: %s',
    (_name, testCase, grammar) => {
      let state = GBNF(grammar);
      for (const char of testCase) {
        state = state.add(char);
      }
      expect(state).toBeDefined();
    },
  );
});
