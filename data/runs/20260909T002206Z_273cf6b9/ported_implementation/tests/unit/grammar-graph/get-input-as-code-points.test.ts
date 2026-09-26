import { describe, expect, test } from 'vitest';
import { getInputAsCodePoints } from '../../../src/grammar-graph/get-input-as-code-points.ts';

describe('get_input_as_code_points', () => {
  test('it returns code points for a string', () => {
    expect(getInputAsCodePoints('abc')).toStrictEqual([97, 98, 99]);
  });

  test('it returns code points for a number', () => {
    expect(getInputAsCodePoints(99)).toStrictEqual([99]);
  });

  test('it returns code points for an array of numbers', () => {
    expect(getInputAsCodePoints([99, 100, 101])).toStrictEqual([99, 100, 101]);
  });
});
