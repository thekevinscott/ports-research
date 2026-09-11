import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { buildErrorPosition } from '../src/utils/errors/buildErrorPosition.ts';
import type { ValidInput } from '../src/utils/errors/errorsTypes.ts';
import { getInputAsString } from '../src/utils/errors/getInputAsString.ts';
import {
  GRAMMAR_PARSER_ERROR_HEADER_MESSAGE,
  GrammarParseError,
} from '../src/utils/errors/grammarParseError.ts';
import {
  INPUT_PARSER_ERROR_HEADER_MESSAGE,
  InputParseError,
} from '../src/utils/errors/inputParseError.ts';

describe('buildErrorPosition', () => {
  const cases: [string, number, [string, string]][] = [
    ['root ::= "foo"', 1, ['root ::= "foo"', ' ^']],
    ['root ::= "foo"', 5, ['root ::= "foo"', '     ^']],
    ['aa\nbb', 1, ['aa', ' ^']],
    ['aa\nbb', 2, ['aa\nbb', '^']],
    ['aa\nbb', 3, ['aa\nbb', ' ^']],
    ['aa\nbb\ncc', 3, ['aa\nbb', ' ^']],
    ['aa\nbb\ncc', 4, ['aa\nbb\ncc', '^']],
    ['aa\nbb\ncc', 5, ['aa\nbb\ncc', ' ^']],
    ['aa\nbb\ncc\ndd', 6, ['bb\ncc\ndd', '^']],
    ['aa\nbb\ncc\ndd\nee', 9, ['cc\ndd\nee', ' ^']],
  ];

  for (const [grammar, pos, [grammarOut, posOut]] of cases) {
    it(`correctly shows position ${pos} for ${JSON.stringify(grammar)}`, () => {
      assert.deepStrictEqual(buildErrorPosition(grammar, pos), [...grammarOut.split('\n'), posOut]);
    });
  }

  it('renders a message for empty input', () => {
    assert.deepStrictEqual(buildErrorPosition('', 0), ['No input provided']);
  });
});

describe('getInputAsString', () => {
  const cases: [ValidInput, string][] = [
    ['hello', 'hello'],
    [[104, 101, 108, 108, 111], 'hello'],
    [104, 'h'],
    [128512, '😀'],
    [[128512, 128513], '😀😁'],
  ];

  for (const [input, expected] of cases) {
    it(`converts ${JSON.stringify(input)} to ${JSON.stringify(expected)}`, () => {
      assert.equal(getInputAsString(input), expected);
    });
  }
});

describe('GrammarParseError', () => {
  it('renders a message', () => {
    const grammar = 'aa\nbb\ncc\ndd\nee';
    const pos = 5;
    const reason = 'reason';
    const err = new GrammarParseError(grammar, pos, reason);
    assert.equal(
      err.message,
      [GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason), '', 'aa', 'bb', 'cc', ' ^'].join('\n'),
    );
  });

  it('keeps the grammar, position and reason', () => {
    const err = new GrammarParseError('root ::= "foo"', 3, 'reason');
    assert.equal(err.grammar, 'root ::= "foo"');
    assert.equal(err.pos, 3);
    assert.equal(err.reason, 'reason');
    assert.ok(err instanceof Error);
  });
});

describe('InputParseError', () => {
  it('renders a message', () => {
    const input = 'some input';
    const err = new InputParseError(input, 1);
    assert.equal(
      err.message,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', input, ' ^'].join('\n'),
    );
  });

  it('renders a message for a code point', () => {
    const err = new InputParseError('a', 0);
    assert.equal(err.message, [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', 'a', '^'].join('\n'));
  });

  it('renders a message for code points', () => {
    const err = new InputParseError('abcd', 2);
    assert.equal(err.message, [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', 'abcd', '  ^'].join('\n'));
  });

  it('exposes the combined source and the most-recent-input-only error', () => {
    const err = new InputParseError('cd', 1, 'ab');
    assert.equal(err.src, 'abcd');
    assert.equal(err.message, [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', 'abcd', '   ^'].join('\n'));
    assert.equal(
      err.errorForMostRecentInput,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, '', 'cd', ' ^'].join('\n'),
    );
  });
});
