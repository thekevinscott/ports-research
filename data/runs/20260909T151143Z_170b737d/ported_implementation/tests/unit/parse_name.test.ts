import assert from "node:assert/strict";
import { test } from "node:test";

import { PARSE_NAME_ERROR, parse_name } from "../../src/rules_builder/parse_name.ts";
import { GrammarParseError } from "../../src/utils/errors/index.ts";

test("returns the correct name when encountering a valid name", () => {
  const src = "validName";
  assert.equal(parse_name(src, 0), src);
});

test("returns the correct name when starting at a non-zero position", () => {
  assert.equal(parse_name("123validName", 3), "validName");
});

test("accepts the valid name separators", () => {
  assert.equal(parse_name("foo-bar_baz ::= x", 0), "foo-bar_baz");
});

test("throws when encountering an invalid name", () => {
  const src = "123";
  assert.throws(
    () => parse_name(src, 0),
    (error: unknown) => {
      assert.ok(error instanceof GrammarParseError);
      assert.equal(String(error), String(new GrammarParseError(src, 0, PARSE_NAME_ERROR)));
      return true;
    },
  );
});
