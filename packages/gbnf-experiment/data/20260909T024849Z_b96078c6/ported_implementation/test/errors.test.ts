import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { buildErrorPosition } from "../src/utils/errors/build-error-position.ts";
import { getInputAsString } from "../src/utils/errors/get-input-as-string.ts";
import {
  GrammarParseError,
  GRAMMAR_PARSER_ERROR_HEADER_MESSAGE,
} from "../src/utils/errors/grammar-parse-error.ts";
import {
  InputParseError,
  INPUT_PARSER_ERROR_HEADER_MESSAGE,
} from "../src/utils/errors/input-parse-error.ts";

describe("buildErrorPosition", () => {
  const cases: [string, number, string[]][] = [
    ['root ::= "foo"', 0, ['root ::= "foo"', "^"]],
    ['root ::= "foo"', 4, ['root ::= "foo"', "    ^"]],
    ["aa\nbb", 0, ["aa", "^"]],
    ["aa\nbb", 3, ["aa", "bb", " ^"]],
    ["aa\nbb\ncc", 5, ["aa", "bb", "cc", " ^"]],
    ["aa\nbb\ncc\ndd", 7, ["bb", "cc", "dd", " ^"]],
    ["aa\nbb\ncc\ndd\nee", 9, ["cc", "dd", "ee", " ^"]],
  ];

  for (const [grammar, pos, expected] of cases) {
    it(`shows the position for ${JSON.stringify(grammar)} at ${pos}`, () => {
      assert.deepEqual(buildErrorPosition(grammar, pos), expected);
    });
  }

  it("renders a message for empty input", () => {
    assert.deepEqual(buildErrorPosition("", 0), ["No input provided"]);
  });

  it("never shows more than three lines of context", () => {
    assert.equal(buildErrorPosition("aa\nbb\ncc\ndd\nee", 9).length, 4);
  });
});

describe("getInputAsString", () => {
  const cases: [string | number | number[], string][] = [
    ["hello", "hello"],
    [[104, 101, 108, 108, 111], "hello"],
    [104, "h"],
    [128512, "😀"],
    [[128512, 128513], "😀😁"],
  ];

  for (const [input, expected] of cases) {
    it(`converts ${JSON.stringify(input)} to a string`, () => {
      assert.equal(getInputAsString(input), expected);
    });
  }
});

describe("GrammarParseError", () => {
  it("renders a message", () => {
    const err = new GrammarParseError("aa\nbb\ncc\ndd\nee", 5, "reason");
    assert.equal(
      err.message,
      [GRAMMAR_PARSER_ERROR_HEADER_MESSAGE("reason"), "", "aa", "bb", "cc", " ^"].join("\n"),
    );
  });

  it("retains the grammar, position and reason", () => {
    const err = new GrammarParseError("root ::= x", 4, "reason");
    assert.equal(err.grammar, "root ::= x");
    assert.equal(err.pos, 4);
    assert.equal(err.reason, "reason");
    assert.ok(err instanceof Error);
    assert.equal(err.name, "GrammarParseError");
  });
});

describe("InputParseError", () => {
  it("renders a message", () => {
    assert.equal(
      new InputParseError("some input", 1).message,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, "", "some input", " ^"].join("\n"),
    );
  });

  it("renders a message for a code point", () => {
    assert.equal(
      new InputParseError(97, 0).message,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, "", "a", "^"].join("\n"),
    );
  });

  it("renders a message for code points", () => {
    assert.equal(
      new InputParseError([97, 98, 99, 100], 2).message,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, "", "abcd", "  ^"].join("\n"),
    );
  });

  it("offsets the position by the previous input", () => {
    const err = new InputParseError("cd", 1, "ab");
    assert.equal(
      err.message,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, "", "abcd", "   ^"].join("\n"),
    );
    assert.equal(err.src, "abcd");
    assert.equal(
      err.errorForMostRecentInput,
      [INPUT_PARSER_ERROR_HEADER_MESSAGE, "", "cd", " ^"].join("\n"),
    );
    assert.equal(err.name, "InputParseError");
  });
});
