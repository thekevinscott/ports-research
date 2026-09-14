import { describe, expect, test } from 'vitest';
import type { ValidInput } from '../../../../src/index.ts';
import { getInputAsString } from '../../../../src/utils/errors/get-input-as-string.ts';

describe('get_input_as_string', () => {
  test.each([
    ['hello', 'hello'],
    [[104, 101, 108, 108, 111], 'hello'],
    [104, 'h'],
    [0x1F600, '😀'],
    [[0x1F600, 0x1F601], '😀😁'],
  ] as [ValidInput, string][])(
    'it correctly converts %j to a string',
    (input, expected) => {
      expect(getInputAsString(input)).toBe(expected);
    },
  );
});
