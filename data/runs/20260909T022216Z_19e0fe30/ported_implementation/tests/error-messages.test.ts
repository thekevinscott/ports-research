import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { GBNF, GrammarParseError, InputParseError } from '../src/index.js';

/**
 * The translated error tests build their expectation with this package's own
 * error classes, so they would still pass if the rendered message drifted from
 * the reference. These cases compare against error strings recorded from the
 * python reference implementation (tools/record-reference-errors.py).
 */
const here = dirname(fileURLToPath(import.meta.url));

interface ReferenceErrors {
  grammar: { grammar: string; message: string }[];
  input: {
    grammar: string;
    input: string;
    message: string;
    errorForMostRecentInput: string;
    src: string;
  }[];
  incremental: {
    message: string;
    errorForMostRecentInput: string;
    src: string;
  };
}

const reference = JSON.parse(
  readFileSync(join(here, 'fixtures', 'reference-errors.json'), 'utf8'),
) as ReferenceErrors;

describe('error messages match the reference implementation', () => {
  it.each(reference.grammar.map((c, idx) => [`#${idx}`, c]))(
    'renders the same GrammarParseError: %s',
    (_name, testCase) => {
      const { grammar, message } = testCase as ReferenceErrors['grammar'][0];
      let thrown: unknown;
      try {
        GBNF(grammar);
      } catch (err) {
        thrown = err;
      }
      expect(thrown).toBeInstanceOf(GrammarParseError);
      expect(String(thrown)).toBe(message);
      expect((thrown as GrammarParseError).message).toBe(message);
    },
  );

  it.each(reference.input.map((c, idx) => [`#${idx}`, c]))(
    'renders the same InputParseError: %s',
    (_name, testCase) => {
      const { grammar, input, message, errorForMostRecentInput, src } =
        testCase as ReferenceErrors['input'][0];
      const state = GBNF(grammar);
      let thrown: unknown;
      try {
        state.add(input);
      } catch (err) {
        thrown = err;
      }
      expect(thrown).toBeInstanceOf(InputParseError);
      const err = thrown as InputParseError;
      expect(String(err)).toBe(message);
      expect(err.message).toBe(message);
      expect(err.errorForMostRecentInput).toBe(errorForMostRecentInput);
      expect(err.src).toBe(src);
    },
  );

  it('renders the same InputParseError for incremental input', () => {
    const state = GBNF('root ::= "bar"').add('b').add('a');
    let thrown: unknown;
    try {
      state.add('z');
    } catch (err) {
      thrown = err;
    }
    expect(thrown).toBeInstanceOf(InputParseError);
    const err = thrown as InputParseError;
    expect(String(err)).toBe(reference.incremental.message);
    expect(err.errorForMostRecentInput).toBe(
      reference.incremental.errorForMostRecentInput,
    );
    expect(err.src).toBe(reference.incremental.src);
  });
});
