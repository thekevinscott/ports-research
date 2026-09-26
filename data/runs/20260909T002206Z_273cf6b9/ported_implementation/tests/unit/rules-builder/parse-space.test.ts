import { describe, expect, test } from 'vitest';
import { parseSpace } from '../../../src/rules-builder/parse-space.ts';

describe('parse_space', () => {
  test('return input string when no whitespace or comments', () => {
    const input = 'abcdefghijk';
    expect(input.slice(parseSpace(input, 0, true))).toBe(input);
  });

  test('skip leading spaces and tabs', () => {
    const input = '   \t   abcdefghijk';
    expect(input.slice(parseSpace(input, 0, true))).toBe('abcdefghijk');
  });

  test('skip leading newline characters when newline_ok true', () => {
    const input = '\n\n\r\n\r\nabcdefghijk';
    expect(input.slice(parseSpace(input, 0, true))).toBe('abcdefghijk');
  });

  test('not skip leading newline characters when newline_ok false', () => {
    const input = '\n\n\r\n\r\nabcdefghijk';
    expect(input.slice(parseSpace(input, 0, false))).toBe('\n\n\r\n\r\nabcdefghijk');
  });

  test('skip comments and leading spaces', () => {
    const input = '  # This is a comment\n\t   abcdefghijk';
    expect(input.slice(parseSpace(input, 0, true))).toBe('abcdefghijk');
  });

  test('skip comments and leading newline characters when newline_ok true', () => {
    const input = '\n\n # This is a comment\n\r\n\r\nabcdefghijk';
    expect(input.slice(parseSpace(input, 0, true))).toBe('abcdefghijk');
  });

  test('skip comments and leading newline characters when newline_ok false', () => {
    const input = '\n\n # This is a comment\n\r\n\r\nabcdefghijk';
    expect(input.slice(parseSpace(input, 0, false))).toBe('\n\n # This is a comment\n\r\n\r\nabcdefghijk');
  });

  test('return empty string if input all whitespace and comments', () => {
    const input = '  \t# Comment\n# Another comment\n\n';
    expect(input.slice(parseSpace(input, 0, true))).toBe('');
  });

  test('return empty string for empty input string', () => {
    const input = '';
    expect(input.slice(parseSpace(input, 0, true))).toBe('');
  });
});
