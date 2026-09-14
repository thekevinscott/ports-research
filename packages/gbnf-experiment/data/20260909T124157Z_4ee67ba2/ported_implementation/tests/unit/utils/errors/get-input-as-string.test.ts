import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { getInputAsString } from '../../../../src/utils/errors/get-input-as-string.ts';
import type { ValidInput } from '../../../../src/index.ts';

const CASES: [ValidInput, string][] = [
  ['hello', 'hello'],
  [[104, 101, 108, 108, 111], 'hello'],
  [104, 'h'],
  [0x1f600, '😀'],
  [[0x1f600, 0x1f601], '😀😁'],
];

describe('get input as string', () => {
  for (const [input, expected] of CASES) {
    test(`it correctly converts ${JSON.stringify(input)} to a string`, () => {
      assert.equal(getInputAsString(input), expected);
    });
  }
});
