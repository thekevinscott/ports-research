import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { basename, extname, join } from 'node:path';
import { describe, test } from 'node:test';
import { GBNF } from '../../src/index.ts';
import { grammarsDir } from '../helpers.ts';

interface GrammarCase {
  key: string;
  testCase: string;
  grammar: string;
}

const loadCases = (): GrammarCase[] => {
  const cases: GrammarCase[] = [];
  const grammarFiles = readdirSync(grammarsDir)
    .filter(file => extname(file) === '.gbnf')
    .sort();
  for (const file of grammarFiles) {
    const key = basename(file, '.gbnf');
    const grammar = readFileSync(join(grammarsDir, file), 'utf-8');
    const testCases: string[] = JSON.parse(
      readFileSync(join(grammarsDir, `${key}.json`), 'utf-8'),
    );
    for (const testCase of testCases) {
      cases.push({ key, testCase, grammar });
    }
  }
  if (cases.length === 0) {
    throw new Error('No grammar test cases found');
  }
  return cases;
};

describe('grammars', () => {
  describe('it parses a known valid grammar', () => {
    for (const [index, { key, testCase, grammar }] of loadCases().entries()) {
      test(`${key} [${index}]: ${JSON.stringify(testCase)}`, () => {
        let state = GBNF(grammar);
        for (const char of testCase) {
          state = state.add(char);
        }
        assert.ok(state.size >= 0);
      });
    }
  });
});
