import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { parseChar } from '../../../src/rules-builder/parse-char.ts';
import { GrammarParseError } from '../../../src/utils/errors/index.ts';
import { ord } from '../../helpers.ts';

const PREFIX_LENGTH = 'root ::= "'.length;

const SIMPLE: [string, string, number][] = [
  ['escaped 8-bit unicode char', 'a', ord('a')],
  ['escaped 8-bit unicode char', '9', ord('9')],
];

const COMPLEX: [string, string, number, number][] = [
  ['escaped 8-bit unicode char', '\\x2A', ord('\x2A'), 4],
  ['escaped 16-bit unicode char', '\\u006F', ord('o'), 6],
  ['escaped 32-bit unicode char', '\\U0001F4A9', 128169, 10],
  ['escaped tab char', '\\t', ord('\t'), 2],
  ['escaped new line char', '\\n', ord('\n'), 2],
  ['escaped \r char', '\\r', ord('\r'), 2],
  ['escaped quote char', '\\"', ord('"'), 2],
  ['escaped [ char', '\\[', ord('['), 2],
  ['escaped ] char', '\\]', ord(']'), 2],
  ['escaped \\ char', '\\\\', ord('\\'), 2],
];

const RAISES: [string, number][] = [
  ['', 0],
  ['a', 1],
  ['a', 2],
];

describe('parse char', () => {
  for (const [index, [description, char, codePoint]] of SIMPLE.entries()) {
    test(`simple: ${description} [${index}]`, () => {
      const grammar = `root ::= "${char}" "foo"`;
      assert.deepStrictEqual(parseChar(grammar, PREFIX_LENGTH), [codePoint, 1]);
    });
  }

  for (const [description, escapedChar, codePoint, incPos] of COMPLEX) {
    test(`complex: ${description}`, () => {
      const grammar = `root ::= "${escapedChar}" "foo"`;
      assert.deepStrictEqual(parseChar(grammar, PREFIX_LENGTH), [codePoint, incPos]);
    });
  }

  for (const [input, pos] of RAISES) {
    test(`raises for ${JSON.stringify(input)} @ ${pos}`, () => {
      assert.throws(() => parseChar(input, pos), GrammarParseError);
    });
  }
});
