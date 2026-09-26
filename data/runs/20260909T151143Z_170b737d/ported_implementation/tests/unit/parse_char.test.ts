import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { parse_char } from "../../src/rules_builder/parse_char.ts";
import { GrammarParseError } from "../../src/utils/errors/index.ts";

const PREFIX = 'root ::= "';

describe("parse_char", () => {
  describe("simple characters", () => {
    for (const char of ["a", "9"]) {
      it(`parses ${JSON.stringify(char)}`, () => {
        const grammar = `${PREFIX}${char}" "foo"`;
        assert.deepStrictEqual(parse_char(grammar, PREFIX.length), [
          char.codePointAt(0),
          1,
        ]);
      });
    }
  });

  describe("escaped characters", () => {
    const cases: Array<[string, string, number, number]> = [
      ["escaped 8-bit unicode char", "\\x2A", "*".codePointAt(0) as number, 4],
      ["escaped 16-bit unicode char", "\\u006F", "o".codePointAt(0) as number, 6],
      ["escaped 32-bit unicode char", "\\U0001F4A9", 128169, 10],
      ["escaped tab char", "\\t", 9, 2],
      ["escaped new line char", "\\n", 10, 2],
      ["escaped carriage return char", "\\r", 13, 2],
      ["escaped quote char", '\\"', 34, 2],
      ["escaped [ char", "\\[", 91, 2],
      ["escaped ] char", "\\]", 93, 2],
      ["escaped \\ char", "\\\\", 92, 2],
    ];

    for (const [description, escaped_char, code_point, inc_pos] of cases) {
      it(description, () => {
        const grammar = `${PREFIX}${escaped_char}" "foo"`;
        assert.deepStrictEqual(parse_char(grammar, PREFIX.length), [code_point, inc_pos]);
      });
    }
  });

  describe("out of bounds", () => {
    const cases: Array<[string, number]> = [
      ["", 0],
      ["a", 1],
      ["a", 2],
    ];

    for (const [input, pos] of cases) {
      it(`throws for ${JSON.stringify(input)} at ${pos}`, () => {
        assert.throws(() => parse_char(input, pos), GrammarParseError);
      });
    }
  });

  it("throws on an unknown escape", () => {
    assert.throws(() => parse_char('"\\q"', 1), /Unknown escape/);
  });
});
