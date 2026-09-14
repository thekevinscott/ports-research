import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  GBNF,
  GrammarParseError,
  InputParseError,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../../src/index.ts";
import { KeyError } from "../../src/utils/python_compat.ts";

const values = (state: Iterable<unknown>): unknown[] =>
  [...state].map((rule) =>
    rule instanceof RuleEnd ? "END" : (rule as RuleChar | RuleCharExclude).value,
  );

describe("GBNF", () => {
  it("exposes the rules accepted at the start of the grammar", () => {
    const state = GBNF('root ::= "foo"');
    assert.deepStrictEqual(values(state), [[102]]);
    assert.equal(state.size, 1);
    assert.equal(state.grammar, 'root ::= "foo"');
  });

  it("accepts an initial string", () => {
    assert.deepStrictEqual(values(GBNF('root ::= "foo"', "fo")), [[111]]);
  });

  it("advances through the grammar one character at a time", () => {
    let state = GBNF('root ::= "foo"');
    state = state.add("f");
    assert.deepStrictEqual(values(state), [[111]]);
    state = state.add("o");
    assert.deepStrictEqual(values(state), [[111]]);
    state = state.add("o");
    assert.deepStrictEqual(values(state), ["END"]);
  });

  it("handles alternates", () => {
    const state = GBNF('root  ::= "f" ("b" | "a")').add("f");
    assert.deepStrictEqual(values(state).sort(), [[97], [98]]);
  });

  it("handles character classes and ranges", () => {
    const state = GBNF("root  ::= [a-zA-Z0-9]");
    assert.deepStrictEqual(values(state), [
      [
        [97, 122],
        [65, 90],
        [48, 57],
      ],
    ]);
    assert.deepStrictEqual(values(state.add("q")), ["END"]);
  });

  it("handles negated character classes", () => {
    const state = GBNF("root ::= [^0-9]");
    const [rule] = [...state];
    assert.ok(rule instanceof RuleCharExclude);
    assert.deepStrictEqual(values(state.add("a")), ["END"]);
    assert.throws(() => state.add("5"), InputParseError);
  });

  it("parses a JSON-ish grammar", () => {
    const grammar = [
      "root   ::= object",
      'object ::= "{" ws ( string ":" ws value ("," ws string ":" ws value)* )? "}" ws',
      'value  ::= object | string | "true" | "false" | "null"',
      'string ::= "\\"" [^"]* "\\""',
      "ws     ::= [ \\t\\n]*",
    ].join("\n");
    let state = GBNF(grammar);
    for (const char of '{"a":"b"}') {
      state = state.add(char);
    }
    assert.ok([...state].some((rule) => rule instanceof RuleEnd));
  });

  it("reports where the input stopped matching", () => {
    const state = GBNF('root ::= "foo"').add("f");
    assert.throws(
      () => state.add("x"),
      (error: unknown) => {
        assert.ok(error instanceof InputParseError);
        assert.equal(error.message, "Failed to parse input string:\n\nfx\n ^");
        assert.equal(error.error_for_most_recent_input, "Failed to parse input string:\n\nx\n^");
        return true;
      },
    );
  });

  it("rejects a non-string grammar", () => {
    assert.throws(() => GBNF(1 as unknown as string), /grammar must be a string/);
  });

  it("rejects a non-string initial input", () => {
    assert.throws(
      () => GBNF('root ::= "foo"', 1 as unknown as string),
      /input must be a string/,
    );
  });

  it("reports an empty grammar", () => {
    assert.throws(
      () => GBNF(""),
      (error: unknown) => {
        assert.ok(error instanceof GrammarParseError);
        assert.equal(
          error.message,
          "Failed to parse grammar: No rules were found\n\nNo input provided",
        );
        return true;
      },
    );
  });

  it("reports a grammar with no root rule", () => {
    assert.throws(() => GBNF('foo ::= "bar"'), KeyError);
  });
});
