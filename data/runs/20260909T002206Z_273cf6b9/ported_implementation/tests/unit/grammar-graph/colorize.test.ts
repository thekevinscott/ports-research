import { expect, test } from 'vitest';
import { Color, colorize } from '../../../src/grammar-graph/colorize.ts';

test('colorize strings', () => {
  expect(colorize('hello', Color.BLUE)).toBe('\x1b[34mhello');
  expect(colorize('test', Color.CYAN)).toBe('\x1b[36mtest');
  expect(colorize('example', Color.GREEN)).toBe('\x1b[32mexample');
});

test('colorize numbers', () => {
  expect(colorize(123, Color.RED)).toBe('\x1b[31m123');
  expect(colorize(456, Color.GRAY)).toBe('\x1b[90m456');
  expect(colorize(789, Color.YELLOW)).toBe('\x1b[33m789');
});
