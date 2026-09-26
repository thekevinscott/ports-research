import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { parseSpace } from '../../../src/rules-builder/parse-space.ts';

describe('parse space', () => {
  test('return input string when no whitespace or comments', () => {
    const inputStr = 'abcdefghijk';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, true)), inputStr);
  });

  test('skip leading spaces and tabs', () => {
    const inputStr = '   \t   abcdefghijk';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, true)), 'abcdefghijk');
  });

  test('skip leading newline characters when newline_ok true', () => {
    const inputStr = '\n\n\r\n\r\nabcdefghijk';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, true)), 'abcdefghijk');
  });

  test('not skip leading newline characters when newline_ok false', () => {
    const inputStr = '\n\n\r\n\r\nabcdefghijk';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, false)), '\n\n\r\n\r\nabcdefghijk');
  });

  test('skip comments and leading spaces', () => {
    const inputStr = '  # This is a comment\n\t   abcdefghijk';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, true)), 'abcdefghijk');
  });

  test('skip comments and leading newline characters when newline_ok true', () => {
    const inputStr = '\n\n # This is a comment\n\r\n\r\nabcdefghijk';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, true)), 'abcdefghijk');
  });

  test('skip comments and leading newline characters when newline_ok false', () => {
    const inputStr = '\n\n # This is a comment\n\r\n\r\nabcdefghijk';
    assert.equal(
      inputStr.slice(parseSpace(inputStr, 0, false)),
      '\n\n # This is a comment\n\r\n\r\nabcdefghijk',
    );
  });

  test('return empty string if input all whitespace and comments', () => {
    const inputStr = '  \t# Comment\n# Another comment\n\n';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, true)), '');
  });

  test('return empty string for empty input string', () => {
    const inputStr = '';
    assert.equal(inputStr.slice(parseSpace(inputStr, 0, true)), '');
  });
});
