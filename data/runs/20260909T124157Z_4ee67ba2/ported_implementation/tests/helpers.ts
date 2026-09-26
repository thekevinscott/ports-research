import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type ResolvedRule,
} from '../src/index.ts';

const HERE = dirname(fileURLToPath(import.meta.url));

export interface ParametrizeTable {
  argnames: string[];
  cases: unknown[][];
}

/**
 * Load a parametrize table extracted from the Python suite.
 * Regenerate the fixtures with `python3 tests/tools/extract-cases.py`.
 */
export const loadTable = (fixture: string, testName: string): unknown[][] => {
  const tables: Record<string, ParametrizeTable> = JSON.parse(
    readFileSync(join(HERE, 'fixtures', `${fixture}.json`), 'utf-8'),
  );
  const table = tables[testName];
  if (!table) {
    throw new Error(`No parametrize table for ${fixture}::${testName}`);
  }
  return table.cases;
};

export interface ExpectedRule {
  type: 'char' | 'char_exclude' | 'end';
  value?: (number | Range)[];
}

/** The Python suite's `transformed_expected_dict`. */
export const transformExpected = (e: ExpectedRule): ResolvedRule => {
  switch (e.type) {
    case 'char':
      return new RuleChar(e.value as (number | Range)[]);
    case 'char_exclude':
      return new RuleCharExclude(e.value as (number | Range)[]);
    case 'end':
      return new RuleEnd();
    default:
      throw new Error(`Unknown type found in expectation array: ${e.type}`);
  }
};

/** The Python suite's `sorted(..., key=lambda r: json.dumps(r.__dict__))`. */
export const sortRules = (rules: ResolvedRule[]): ResolvedRule[] =>
  [...rules].sort((a, b) => {
    const [ka, kb] = [JSON.stringify(a.toDict()), JSON.stringify(b.toDict())];
    if (ka < kb) {
      return -1;
    }
    return ka > kb ? 1 : 0;
  });

/** A stable, readable label for a test case, standing in for pytest's case ids. */
export const label = (...parts: unknown[]): string =>
  parts.map(part => JSON.stringify(part)).join(' | ');

export const ord = (char: string): number => char.codePointAt(0) as number;

export const grammarsDir = join(HERE, 'grammars');
