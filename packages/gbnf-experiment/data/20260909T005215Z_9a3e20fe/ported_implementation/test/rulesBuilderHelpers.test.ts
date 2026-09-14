import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { isWordChar } from '../src/rulesBuilder/isWordChar.ts';
import { parseChar } from '../src/rulesBuilder/parseChar.ts';
import { PARSE_NAME_ERROR, parseName } from '../src/rulesBuilder/parseName.ts';
import { GrammarParseError } from '../src/utils/errors/index.ts';

const ord = (char: string): number => char.codePointAt(0) as number;

describe('isWordChar', () => {
  it('returns true for lowercase letters', () => {
    assert.ok(isWordChar('a'));
    assert.ok(isWordChar('z'));
  });

  it('returns true for uppercase letters', () => {
    assert.ok(isWordChar('A'));
    assert.ok(isWordChar('Z'));
  });

  it('returns false for digits', () => {
    assert.ok(!isWordChar('0'));
    assert.ok(!isWordChar('9'));
  });

  it('returns false for non-word characters', () => {
    assert.ok(!isWordChar('-'));
    assert.ok(!isWordChar('@'));
    assert.ok(!isWordChar('_'));
    assert.ok(!isWordChar('?'));
    assert.ok(!isWordChar(' '));
  });
});

describe('parseName', () => {
  it('returns the correct name when encountering a valid name', () => {
    const src = 'validName';
    assert.equal(parseName(src, 0), src);
  });

  it('returns the correct name when starting at a non-zero position', () => {
    const src = '123validName';
    assert.equal(parseName(src, 3), 'validName');
  });

  it('throws an error when encountering an invalid name', () => {
    const src = '123';
    assert.throws(
      () => parseName(src, 0),
      (err: unknown) => {
        assert.ok(err instanceof GrammarParseError);
        assert.equal(err.message, new GrammarParseError(src, 0, PARSE_NAME_ERROR).message);
        return true;
      },
    );
  });
});

describe('parseChar', () => {
  const simpleCases: [string, string, number][] = [
    ['escaped 8-bit unicode char', 'a', ord('a')],
    ['escaped 8-bit unicode char', '9', ord('9')],
  ];

  for (const [description, char, codePoint] of simpleCases) {
    it(`parses a simple char: ${description} (${char})`, () => {
      const grammar = `root ::= "${char}" "foo"`;
      assert.deepStrictEqual(parseChar(grammar, 'root ::= "'.length), [codePoint, 1]);
    });
  }

  const complexCases: [string, string, number, number][] = [
    ['escaped 8-bit unicode char', '\\x2A', ord('*'), 4],
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

  for (const [description, escapedChar, codePoint, incPos] of complexCases) {
    it(`parses an escaped char: ${description} (${escapedChar})`, () => {
      const grammar = `root ::= "${escapedChar}" "foo"`;
      assert.deepStrictEqual(parseChar(grammar, 'root ::= "'.length), [codePoint, incPos]);
    });
  }

  const raisesCases: [string, number][] = [
    ['', 0],
    ['a', 1],
    ['a', 2],
  ];

  for (const [input, pos] of raisesCases) {
    it(`throws for input ${JSON.stringify(input)} at position ${pos}`, () => {
      assert.throws(() => parseChar(input, pos), GrammarParseError);
    });
  }

  it('throws on an unknown escape', () => {
    assert.throws(() => parseChar('\\q', 0), /Unknown escape at \\/u);
  });
});
