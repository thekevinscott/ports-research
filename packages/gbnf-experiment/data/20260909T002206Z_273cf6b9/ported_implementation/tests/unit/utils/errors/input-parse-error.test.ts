import { describe, expect, test } from 'vitest';
import {
  INPUT_PARSER_ERROR_HEADER_MESSAGE,
  InputParseError,
} from '../../../../src/utils/errors/input-parse-error.ts';

describe('input_parse_error', () => {
  test('it renders a message', () => {
    const input = 'some input';
    const pos = 1;
    const err = new InputParseError(input, pos);
    expect(err.message).toBe([
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      input,
      ' ^',
    ].join('\n'));
  });

  test('it renders a message for a code point', () => {
    const err = new InputParseError('a', 0);
    expect(err.message).toBe([
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      'a',
      '^',
    ].join('\n'));
  });

  test('it renders a message for code points', () => {
    const err = new InputParseError('abcd', 2);
    expect(err.message).toBe([
      INPUT_PARSER_ERROR_HEADER_MESSAGE,
      '',
      'abcd',
      '  ^',
    ].join('\n'));
  });
});
