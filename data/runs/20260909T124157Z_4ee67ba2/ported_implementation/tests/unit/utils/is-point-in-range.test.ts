import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { isPointInRange } from '../../../src/utils/is-point-in-range.ts';
import type { Range } from '../../../src/index.ts';

const CASES: [number, Range, boolean][] = [
  [96, [97, 122], false],
  [97, [97, 122], true],
  [98, [97, 122], true],
  [122, [97, 122], true],
  [123, [97, 122], false],
];

describe('is point in range', () => {
  for (const [point, range, expectation] of CASES) {
    test(`${point} in ${JSON.stringify(range)} is ${expectation}`, () => {
      assert.equal(isPointInRange(point, range), expectation);
    });
  }
});
