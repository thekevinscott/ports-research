import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import type { Range } from '../src/grammarGraph/grammarGraphTypes.ts';
import { isPointInRange } from '../src/utils/isPointInRange.ts';

describe('isPointInRange', () => {
  const cases: [number, Range, boolean][] = [
    [96, [97, 122], false],
    [97, [97, 122], true],
    [98, [97, 122], true],
    [122, [97, 122], true],
    [123, [97, 122], false],
  ];

  for (const [point, range, expectation] of cases) {
    it(`checks if point ${point} is in range ${JSON.stringify(range)}`, () => {
      assert.equal(isPointInRange(point, range), expectation);
    });
  }

  it('throws if the point is not an integer', () => {
    assert.throws(() => isPointInRange(1.5, [0, 10]), /point must be an integer/u);
  });
});
