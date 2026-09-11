import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { isWordChar } from '../../../src/rules-builder/is-word-char.ts';

describe('is word char', () => {
  test('should return true for lowercase letters', () => {
    assert.ok(isWordChar('a'));
    assert.ok(isWordChar('z'));
  });

  test('should return true for uppercase letters', () => {
    assert.ok(isWordChar('A'));
    assert.ok(isWordChar('Z'));
  });

  test('should return false for digits', () => {
    assert.ok(!isWordChar('0'));
    assert.ok(!isWordChar('9'));
  });

  test('should return false for non word characters', () => {
    assert.ok(!isWordChar('-'));
    assert.ok(!isWordChar('@'));
    assert.ok(!isWordChar('_'));
    assert.ok(!isWordChar('?'));
    assert.ok(!isWordChar(' '));
  });
});
