import assert from "node:assert/strict";
import { describe, it } from "node:test";

import GBNFDefault, {
  GBNF,
  GrammarParseError,
  InputParseError,
  ParseState,
  RuleChar,
  RuleEnd,
} from "../src/index.ts";
import * as imports from "../src/index.ts";

const codePointsOf = (state: Iterable<{ value?: unknown }>) =>
  [...state].map((rule) => rule.value);

describe("GBNF", () => {
  it("returns a ParseState", () => {
    const state = GBNF('root ::= "foo"');
    assert.ok(state instanceof ParseState);
    assert.equal(state.grammar, 'root ::= "foo"');
  });

  it("is also the default export", () => {
    assert.equal(GBNFDefault, GBNF);
  });

  it("exposes the rules that can come next", () => {
    const state = GBNF('root ::= "foo"');
    assert.equal(state.size, 1);
    const [rule] = [...state];
    assert.ok(rule instanceof RuleChar);
    assert.deepEqual(rule.value, ["f".codePointAt(0)]);
  });

  it("accepts an initial string", () => {
    const state = GBNF('root ::= "foo"', "fo");
    assert.deepEqual(codePointsOf(state), [["o".codePointAt(0)]]);
  });

  it("walks the grammar as input is added", () => {
    let state = GBNF('root ::= "foo"');
    state = state.add("f");
    assert.deepEqual(codePointsOf(state), [["o".codePointAt(0)]]);
    state = state.add("o");
    assert.deepEqual(codePointsOf(state), [["o".codePointAt(0)]]);
    state = state.add("o");
    const [rule] = [...state];
    assert.ok(rule instanceof RuleEnd);
  });

  it("supports alternates", () => {
    const state = GBNF('root ::= "a" | "b" | "c"');
    assert.deepEqual(
      codePointsOf(state).flat().sort(),
      ["a", "b", "c"].map((char) => char.codePointAt(0)),
    );
  });

  it("supports ranges", () => {
    const state = GBNF("root ::= [a-z]");
    assert.deepEqual(codePointsOf(state), [[[97, 122]]]);
    assert.ok(state.add("q") instanceof ParseState);
  });

  it("supports negated character classes", () => {
    const state = GBNF("root ::= [^a-z]");
    assert.ok(state.add("A") instanceof ParseState);
    assert.throws(() => state.add("a"), InputParseError);
  });

  it("supports unicode", () => {
    const state = GBNF("root ::= [ぁ-ゟ]");
    assert.ok(state.add("ぁ") instanceof ParseState);
    assert.throws(() => state.add("a"), InputParseError);
  });

  it("supports astral characters", () => {
    const state = GBNF('root ::= "💩"');
    assert.ok(state.add("💩") instanceof ParseState);
  });

  it("parses a JSON grammar", () => {
    const grammar = `
root   ::= object
value  ::= object | array | string | number | ("true" | "false" | "null") ws
object ::=
  "{" ws (
            string ":" ws value
    ("," ws string ":" ws value)*
  )? "}" ws
array  ::=
  "[" ws (
            value
    ("," ws value)*
  )? "]" ws
string ::=
  "\\"" (
    [^"\\\\\\x7F\\x00-\\x1F] |
    "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
  )* "\\"" ws
number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws
ws ::= ([ \\t\\n] ws)?
`;
    let state = GBNF(grammar);
    for (const char of '{"a": [1, true]}') {
      state = state.add(char);
    }
    assert.ok(state.size > 0);
  });

  it("throws an InputParseError, with the position marked, for invalid input", () => {
    const state = GBNF('root ::= "foo"');
    assert.throws(() => state.add("b"), (err: Error) => {
      assert.ok(err instanceof InputParseError);
      assert.equal(err.message, ["Failed to parse input string:", "", "b", "^"].join("\n"));
      return true;
    });
  });

  it("includes previous input in the error message", () => {
    const state = GBNF('root ::= "foo"').add("f");
    assert.throws(() => state.add("b"), (err: Error) => {
      assert.equal(err.message, ["Failed to parse input string:", "", "fb", " ^"].join("\n"));
      return true;
    });
  });

  it("throws a GrammarParseError for an invalid grammar", () => {
    assert.throws(() => GBNF("root ::= foo"), GrammarParseError);
  });

  it("throws for a grammar without a root symbol", () => {
    assert.throws(() => GBNF('foo ::= "bar"'), {
      message: /Grammar does not contain a 'root' symbol/,
    });
  });

  it("throws for an empty grammar", () => {
    assert.throws(() => GBNF(""), { message: /No rules were found/ });
  });

  it("prints the graph for a real grammar", () => {
    // The reference implementation crashes here; see PORTING-NOTES.md.
    const { RulesBuilder, buildRuleStack, Graph } = imports;
    const grammar = 'root ::= "foo"';
    const rulesBuilder = new RulesBuilder(grammar);
    const graph = new Graph(
      grammar,
      rulesBuilder.rules.map((rule) => buildRuleStack(rule)),
      rulesBuilder.symbolIds.get("root") as number,
    );
    assert.equal(
      graph.print(),
      "{0,0,0}[f]-> {0,0,1}[o]-> {0,0,2}[o]-> {0,0,3}RuleEnd",
    );
  });

  it("validates its arguments", () => {
    assert.throws(() => GBNF(1 as never), { message: "grammar must be a string" });
    assert.throws(() => GBNF('root ::= "foo"', 1 as never), {
      message: "input must be a string",
    });
  });
});
