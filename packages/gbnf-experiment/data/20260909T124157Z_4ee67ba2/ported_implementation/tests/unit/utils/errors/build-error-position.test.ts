import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { buildErrorPosition } from '../../../../src/utils/errors/build-error-position.ts';

// `\\n` is a literal backslash-n in the source, expanded to a newline by the test body,
// exactly as in the reference suite.
const CASES: [string, number, [string, string]][] = [
  ['root ::= "foo"', 1, ['root ::= "foo"', ' ^']],
  ['root ::= "foo"', 5, ['root ::= "foo"', '     ^']],
  // multi line grammars with pos on first line
  ['aa\\nbb', 1, ['aa', ' ^']],
  // multi line grammars with pos on second line, first character
  ['aa\\nbb', 2, ['aa\\nbb', '^']],
  // multi line grammars with pos on second line, second character
  ['aa\\nbb', 2 + 1, ['aa\\nbb', ' ^']],
  // multi line grammars beyond error with pos on second line
  ['aa\\nbb\\ncc', 2 + 1, ['aa\\nbb', ' ^']],
  // multi line grammars beyond error with pos on third line, first char
  ['aa\\nbb\\ncc', 2 + 2 + 0, ['aa\\nbb\\ncc', '^']],
  // multi line grammars beyond error with pos on third line, second char
  ['aa\\nbb\\ncc', 2 + 2 + 1, ['aa\\nbb\\ncc', ' ^']],
  // multi line grammars beyond error with pos on fourth line, first char
  ['aa\\nbb\\ncc\\ndd', 2 + 2 + 2 + 0, ['bb\\ncc\\ndd', '^']],
  // multi line grammars beyond error with pos on fifth line, second char
  ['aa\\nbb\\ncc\\ndd\\nee', 2 + 2 + 2 + 2 + 1, ['cc\\ndd\\nee', ' ^']],
];

describe('build error position', () => {
  describe('it correctly shows position for single line grammars', () => {
    for (const [grammar, pos, [grammarOut, posOut]] of CASES) {
      test(`${JSON.stringify(grammar)} @ ${pos}`, () => {
        const result = buildErrorPosition(grammar.split('\\n').join('\n'), pos);
        assert.deepStrictEqual(result, [...grammarOut.split('\\n'), posOut]);
      });
    }
  });

  test('it renders a message for empty input', () => {
    assert.deepStrictEqual(buildErrorPosition('', 0), ['No input provided']);
  });
});
