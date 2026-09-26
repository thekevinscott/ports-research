import { describe, expect, test } from 'vitest';
import {
  GRAMMAR_PARSER_ERROR_HEADER_MESSAGE,
  GrammarParseError,
} from '../../../../src/utils/errors/grammar-parse-error.ts';

describe('grammar_parse_error', () => {
  test('it renders a message', () => {
    const grammar = 'aa\\nbb\\ncc\\ndd\\nee';
    const pos = 5;
    const reason = 'reason';
    const err = new GrammarParseError(grammar.split('\\n').join('\n'), pos, reason);
    expect(err.message).toBe([
      GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
      '',
      'aa',
      'bb',
      'cc',
      ' ^',
    ].join('\n'));
  });
});
