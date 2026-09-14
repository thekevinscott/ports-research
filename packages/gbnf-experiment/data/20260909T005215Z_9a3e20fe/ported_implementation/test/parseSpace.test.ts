import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { parseSpace } from '../src/rulesBuilder/parseSpace.ts';

describe('parseSpace', () => {
  it('returns the input string when there is no whitespace or comments', () => {
    const inputStr = 'abcdefghijk';
    const pos = parseSpace(inputStr, 0, true);
    assert.equal(inputStr.slice(pos), inputStr);
  });

  it('skips leading spaces and tabs', () => {
    const inputStr = '   \t   abcdefghijk';
    const pos = parseSpace(inputStr, 0, true);
    assert.equal(inputStr.slice(pos), 'abcdefghijk');
  });

  it('skips leading newline characters when newlineOk is true', () => {
    const inputStr = '\n\n\r\n\r\nabcdefghijk';
    const pos = parseSpace(inputStr, 0, true);
    assert.equal(inputStr.slice(pos), 'abcdefghijk');
  });

  it('does not skip leading newline characters when newlineOk is false', () => {
    const inputStr = '\n\n\r\n\r\nabcdefghijk';
    const pos = parseSpace(inputStr, 0, false);
    assert.equal(inputStr.slice(pos), inputStr);
  });

  it('skips comments and leading spaces', () => {
    const inputStr = '  # This is a comment\n\t   abcdefghijk';
    const pos = parseSpace(inputStr, 0, true);
    assert.equal(inputStr.slice(pos), 'abcdefghijk');
  });

  it('skips comments and leading newline characters when newlineOk is true', () => {
    const inputStr = '\n\n # This is a comment\n\r\n\r\nabcdefghijk';
    const pos = parseSpace(inputStr, 0, true);
    assert.equal(inputStr.slice(pos), 'abcdefghijk');
  });

  it('does not skip comments and leading newline characters when newlineOk is false', () => {
    const inputStr = '\n\n # This is a comment\n\r\n\r\nabcdefghijk';
    const pos = parseSpace(inputStr, 0, false);
    assert.equal(inputStr.slice(pos), inputStr);
  });

  it('returns an empty string if the input is all whitespace and comments', () => {
    const inputStr = '  \t# Comment\n# Another comment\n\n';
    const pos = parseSpace(inputStr, 0, true);
    assert.equal(inputStr.slice(pos), '');
  });

  it('returns an empty string for an empty input string', () => {
    const inputStr = '';
    const pos = parseSpace(inputStr, 0, true);
    assert.equal(inputStr.slice(pos), '');
  });
});
