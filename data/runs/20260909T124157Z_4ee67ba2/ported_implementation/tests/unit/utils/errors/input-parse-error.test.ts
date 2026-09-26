import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import {
  INPUT_PARSER_ERROR_HEADER_MESSAGE,
  InputParseError,
} from '../../../../src/utils/errors/input-parse-error.ts';

describe('input parse error', () => {
  test('it renders a message', () => {
    const input = 'some input';
    const err = new InputParseError(input, 1);
    assert.equal(
      err.message,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', input, ' ^'].join('\n'),
    );
  });

  test('it renders a message for code point', () => {
    const err = new InputParseError('a', 0);
    assert.equal(err.message, [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', 'a', '^'].join('\n'));
  });

  test('it renders a message for code points', () => {
    const err = new InputParseError('abcd', 2);
    assert.equal(
      err.message,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', 'abcd', '  ^'].join('\n'),
    );
  });
});
