import { describe, expect, test } from 'vitest';
import { isWordChar } from '../../../src/rules-builder/is-word-char.ts';

describe('is_word_char', () => {
  test('should return true for lowercase letters', () => {
    expect(isWordChar('a')).toBe(true);
    expect(isWordChar('z')).toBe(true);
  });

  test('should return true for uppercase letters', () => {
    expect(isWordChar('A')).toBe(true);
    expect(isWordChar('Z')).toBe(true);
  });

  test('should return false for digits', () => {
    expect(isWordChar('0')).toBe(false);
    expect(isWordChar('9')).toBe(false);
  });

  test('should return false for non word characters', () => {
    expect(isWordChar('-')).toBe(false);
    expect(isWordChar('@')).toBe(false);
    expect(isWordChar('_')).toBe(false);
    expect(isWordChar('?')).toBe(false);
    expect(isWordChar(' ')).toBe(false);
  });
});
