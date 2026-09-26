import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { getInputAsCodePoints } from '../../../src/grammar-graph/get-input-as-code-points.ts';

describe('get input as code points', () => {
  test('it returns code points for string', () => {
    assert.deepStrictEqual(getInputAsCodePoints('abc'), [97, 98, 99]);
  });

  test('it returns code points for number', () => {
    assert.deepStrictEqual(getInputAsCodePoints(99), [99]);
  });

  test('it returns code points for array of number', () => {
    assert.deepStrictEqual(getInputAsCodePoints([99, 100, 101]), [99, 100, 101]);
  });
});
