import assert from 'node:assert/strict';
import { test } from 'node:test';
import { Color, colorize } from '../../../src/grammar-graph/colorize.ts';

test('colorize strings', () => {
  assert.equal(colorize('hello', Color.BLUE), '\x1b[34mhello');
  assert.equal(colorize('test', Color.CYAN), '\x1b[36mtest');
  assert.equal(colorize('example', Color.GREEN), '\x1b[32mexample');
});

test('colorize numbers', () => {
  assert.equal(colorize(123, Color.RED), '\x1b[31m123');
  assert.equal(colorize(456, Color.GRAY), '\x1b[90m456');
  assert.equal(colorize(789, Color.YELLOW), '\x1b[33m789');
});
