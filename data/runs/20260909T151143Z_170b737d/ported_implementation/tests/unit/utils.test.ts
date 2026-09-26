import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { is_word_char } from "../../src/rules_builder/is_word_char.ts";
import { is_point_in_range } from "../../src/utils/is_point_in_range.ts";
import { validate_non_empty } from "../../src/utils/validate_non_empty.ts";
import { build_error_position } from "../../src/utils/errors/build_error_position.ts";
import { get_input_as_string } from "../../src/utils/errors/get_input_as_string.ts";
import { GrammarParseError, InputParseError } from "../../src/utils/errors/index.ts";
import { json_dumps } from "../../src/utils/python_compat.ts";

describe("is_word_char", () => {
  it("returns true for lowercase letters", () => {
    assert.ok(is_word_char("a"));
    assert.ok(is_word_char("z"));
  });

  it("returns true for uppercase letters", () => {
    assert.ok(is_word_char("A"));
    assert.ok(is_word_char("Z"));
  });

  it("returns false for digits", () => {
    assert.ok(!is_word_char("0"));
    assert.ok(!is_word_char("9"));
  });

  it("returns false for non-word characters", () => {
    for (const char of ["-", "@", "_", "?", " "]) {
      assert.ok(!is_word_char(char), char);
    }
  });
});

describe("is_point_in_range", () => {
  const cases: Array<[number, [number, number], boolean]> = [
    [96, [97, 122], false],
    [97, [97, 122], true],
    [98, [97, 122], true],
    [122, [97, 122], true],
    [123, [97, 122], false],
  ];

  for (const [point, range, expectation] of cases) {
    it(`${point} in [${range}] is ${expectation}`, () => {
      assert.equal(is_point_in_range(point, range), expectation);
    });
  }

  it("rejects non-integer points", () => {
    assert.throws(
      () => is_point_in_range("a" as unknown as number, [97, 122]),
      /point must be an integer/,
    );
  });
});

describe("validate_non_empty", () => {
  it("returns the value when non-empty", () => {
    assert.deepStrictEqual(validate_non_empty([1, 2]), [1, 2]);
  });

  it("throws on an empty value", () => {
    assert.throws(() => validate_non_empty([]), /Value cannot be empty\./);
  });
});

describe("json_dumps", () => {
  it("matches Python's spacing", () => {
    assert.equal(json_dumps([97, 98]), "[97, 98]");
    assert.equal(json_dumps([[97, 122], 65]), "[[97, 122], 65]");
    assert.equal(json_dumps({ type: "RuleChar", value: [65] }), '{"type": "RuleChar", "value": [65]}');
  });
});

describe("get_input_as_string", () => {
  it("passes strings through", () => {
    assert.equal(get_input_as_string("abc"), "abc");
  });

  it("converts a code point", () => {
    assert.equal(get_input_as_string(97), "a");
  });

  it("converts a list of code points", () => {
    assert.equal(get_input_as_string([97, 98, 99]), "abc");
  });
});

describe("build_error_position", () => {
  it("reports missing input", () => {
    assert.deepStrictEqual(build_error_position("", 0), ["No input provided"]);
  });

  it("points at the offending column on a single line", () => {
    assert.deepStrictEqual(build_error_position("root", 4), ["root", "    ^"]);
  });

  it("shows at most three preceding lines", () => {
    const src = "one\ntwo\nthree\nfour\nfive";
    assert.deepStrictEqual(build_error_position(src, 17), ["three", "four", "five", "  ^"]);
  });
});

describe("GrammarParseError", () => {
  it("renders the header, a blank line, and the position", () => {
    const error = new GrammarParseError("root", 4, "Expecting ::= at 4");
    assert.equal(
      error.message,
      "Failed to parse grammar: Expecting ::= at 4\n\nroot\n    ^",
    );
    assert.equal(String(error), error.message);
    assert.equal(error.grammar, "root");
    assert.equal(error.pos, 4);
    assert.equal(error.reason, "Expecting ::= at 4");
  });
});

describe("InputParseError", () => {
  it("renders the combined previous and most recent input", () => {
    const error = new InputParseError([120], 0, [102]);
    assert.equal(error.message, "Failed to parse input string:\n\nfx\n ^");
    assert.equal(String(error), error.message);
    assert.equal(error.src, "fx");
    assert.equal(
      error.error_for_most_recent_input,
      "Failed to parse input string:\n\nx\n^",
    );
  });

  it("defaults previous_input to an empty string", () => {
    const error = new InputParseError([120], 0);
    assert.equal(error.message, "Failed to parse input string:\n\nx\n^");
  });
});
