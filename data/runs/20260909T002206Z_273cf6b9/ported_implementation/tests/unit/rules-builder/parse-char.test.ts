import { describe, expect, test } from 'vitest';
import { parseChar } from '../../../src/rules-builder/parse-char.ts';
import { GrammarParseError } from '../../../src/utils/errors/index.ts';

const PREFIX_LENGTH = 'root ::= "'.length;

describe('parse_char', () => {
  test.each([
    ['escaped 8-bit unicode char', 'a', 'a'.codePointAt(0) as number],
    ['escaped 8-bit unicode char', '9', '9'.codePointAt(0) as number],
  ])('simple: %s (%s)', (_description, char, codePoint) => {
    const grammar = `root ::= "${char}" "foo"`;
    expect(parseChar(grammar, PREFIX_LENGTH)).toStrictEqual([codePoint, 1]);
  });

  test.each([
    ['escaped 8-bit unicode char', '\\x2A', 0x2A, 4],
    ['escaped 16-bit unicode char', '\\u006F', 0x6F, 6],
    ['escaped 32-bit unicode char', '\\U0001F4A9', 128169, 10],
    ['escaped tab char', '\\t', 9, 2],
    ['escaped new line char', '\\n', 10, 2],
    ['escaped \r char', '\\r', 13, 2],
    ['escaped quote char', '\\"', 34, 2],
    ['escaped [ char', '\\[', 91, 2],
    ['escaped ] char', '\\]', 93, 2],
    ['escaped \\ char', '\\\\', 92, 2],
  ])('complex: %s (%s)', (_description, escapedChar, codePoint, incPos) => {
    const grammar = `root ::= "${escapedChar}" "foo"`;
    expect(parseChar(grammar, PREFIX_LENGTH)).toStrictEqual([codePoint, incPos]);
  });

  test.each([
    ['', 0],
    ['a', 1],
    ['a', 2],
  ])('raises for %j at %s', (input, pos) => {
    expect(() => parseChar(input, pos)).toThrow(GrammarParseError);
  });
});
