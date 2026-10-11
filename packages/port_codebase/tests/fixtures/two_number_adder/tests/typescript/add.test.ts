import { describe, expect, test } from 'vitest';

import { add } from 'two_number_adder';

describe('add', () => {
  test('it sums two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  test('it sums a negative and a positive', () => {
    expect(add(-4, 4)).toBe(0);
  });

  test('it sums fractions', () => {
    expect(add(0.5, 0.25)).toBe(0.75);
  });

  test('it rejects a value that is not a number', () => {
    expect(() => add('2' as unknown as number, 3)).toThrow(TypeError);
  });

  test('it rejects a value that is not finite', () => {
    expect(() => add(Number.POSITIVE_INFINITY, 1)).toThrow(TypeError);
  });
});
