import assert from "node:assert/strict";
import { test } from "node:test";

import { parse_space } from "../../src/rules_builder/parse_space.ts";

test("returns the input string when there is no whitespace or comments", () => {
  const input_str = "abcdefghijk";
  const pos = parse_space(input_str, 0, true);
  assert.equal(input_str.slice(pos), input_str);
});

test("skips leading spaces and tabs", () => {
  const input_str = "   \t   abcdefghijk";
  const pos = parse_space(input_str, 0, true);
  assert.equal(input_str.slice(pos), "abcdefghijk");
});

test("skips leading newline characters when newline_ok is true", () => {
  const input_str = "\n\n\r\n\r\nabcdefghijk";
  const pos = parse_space(input_str, 0, true);
  assert.equal(input_str.slice(pos), "abcdefghijk");
});

test("does not skip leading newline characters when newline_ok is false", () => {
  const input_str = "\n\n\r\n\r\nabcdefghijk";
  const pos = parse_space(input_str, 0, false);
  assert.equal(input_str.slice(pos), input_str);
});

test("skips comments and leading spaces", () => {
  const input_str = "  # This is a comment\n\t   abcdefghijk";
  const pos = parse_space(input_str, 0, true);
  assert.equal(input_str.slice(pos), "abcdefghijk");
});

test("skips comments and leading newlines when newline_ok is true", () => {
  const input_str = "\n\n # This is a comment\n\r\n\r\nabcdefghijk";
  const pos = parse_space(input_str, 0, true);
  assert.equal(input_str.slice(pos), "abcdefghijk");
});

test("skips nothing when newline_ok is false and input starts with a newline", () => {
  const input_str = "\n\n # This is a comment\n\r\n\r\nabcdefghijk";
  const pos = parse_space(input_str, 0, false);
  assert.equal(input_str.slice(pos), input_str);
});

test("consumes input that is all whitespace and comments", () => {
  const input_str = "  \t# Comment\n# Another comment\n\n";
  const pos = parse_space(input_str, 0, true);
  assert.equal(input_str.slice(pos), "");
});

test("handles an empty input string", () => {
  const input_str = "";
  const pos = parse_space(input_str, 0, true);
  assert.equal(input_str.slice(pos), "");
});
