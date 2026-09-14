import { describe, expect, test } from 'vitest';

import packageEntry from '../index.ts';
import { GBNF as fromSrcIndex } from '../src/index.ts';
import { GBNF as fromModule } from '../src/gbnf.ts';
import { parseChar } from '../src/rules_builder/parse_char.ts';

/**
 * The package can be imported as a whole (default or named), by its `src`
 * entry point, or file by file. These are all the same implementation.
 */
describe('module resolution', () => {
  test('the default export is the GBNF function', () => {
    expect(packageEntry).toBe(fromModule);
    expect(fromSrcIndex).toBe(fromModule);
  });

  test('individual modules can be imported directly', () => {
    expect(parseChar('a', 0)).toEqual([97, 1]);
  });

  test('the package directory resolves to the entry point', async () => {
    const pkg = await import('../../ported_implementation');
    expect(pkg.GBNF).toBe(fromModule);
    expect(pkg.default).toBe(fromModule);
  });
});
