import { describe, expect, test } from 'vitest';
import type { Range } from '../../../src/index.ts';
import { isPointInRange } from '../../../src/utils/is-point-in-range.ts';

describe('is_point_in_range', () => {
  test.each([
    [96, [97, 122], false],
    [97, [97, 122], true],
    [98, [97, 122], true],
    [122, [97, 122], true],
    [123, [97, 122], false],
  ] as [number, Range, boolean][])(
    'it checks if point %s is in range %s',
    (point, range, expectation) => {
      expect(isPointInRange(point, range)).toBe(expectation);
    },
  );
});
