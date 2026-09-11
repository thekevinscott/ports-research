import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { isWordChar } from "../src/rules-builder/is-word-char.ts";
import { parseChar } from "../src/rules-builder/parse-char.ts";
import { parseName, PARSE_NAME_ERROR } from "../src/rules-builder/parse-name.ts";
import { parseSpace } from "../src/rules-builder/parse-space.ts";
import { getOutElements, RulesBuilder } from "../src/rules-builder/rules-builder.ts";
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
} from "../src/rules-builder/rules-builder-types.ts";
import { SymbolIds } from "../src/rules-builder/symbol-ids.ts";
import { GrammarParseError } from "../src/utils/errors/grammar-parse-error.ts";

describe("isWordChar", () => {
  it("returns true for lowercase letters", () => {
    assert.ok(isWordChar("a"));
    assert.ok(isWordChar("z"));
  });

  it("returns true for uppercase letters", () => {
    assert.ok(isWordChar("A"));
    assert.ok(isWordChar("Z"));
  });

  it("returns false for digits", () => {
    assert.ok(!isWordChar("0"));
    assert.ok(!isWordChar("9"));
  });

  it("returns false for non word characters", () => {
    for (const char of ["-", "@", "_", "?", " "]) {
      assert.ok(!isWordChar(char), `expected ${JSON.stringify(char)} to not be a word char`);
    }
  });
});

describe("parseName", () => {
  it("returns the name when encountering a valid name", () => {
    assert.equal(parseName("validName", 0), "validName");
  });

  it("returns the name when starting at a non-zero position", () => {
    assert.equal(parseName("123validName", 3), "validName");
  });

  it("includes valid separators", () => {
    assert.equal(parseName("foo-bar_baz ::= 'x'", 0), "foo-bar_baz");
  });

  it("throws when encountering an invalid name", () => {
    assert.throws(() => parseName("123", 0), (err: Error) => {
      assert.ok(err instanceof GrammarParseError);
      assert.equal(err.message, new GrammarParseError("123", 0, PARSE_NAME_ERROR).message);
      return true;
    });
  });
});

describe("parseSpace", () => {
  const cases: [string, boolean, string][] = [
    ["abcdefghijk", true, "abcdefghijk"],
    ["   \t   abcdefghijk", true, "abcdefghijk"],
    ["\n\n\r\n\r\nabcdefghijk", true, "abcdefghijk"],
    ["\n\n\r\n\r\nabcdefghijk", false, "\n\n\r\n\r\nabcdefghijk"],
    ["  # This is a comment\n\t   abcdefghijk", true, "abcdefghijk"],
    ["\n\n # This is a comment\n\r\n\r\nabcdefghijk", true, "abcdefghijk"],
    ["\n\n # This is a comment\n\r\n\r\nabcdefghijk", false, "\n\n # This is a comment\n\r\n\r\nabcdefghijk"],
    ["  \t# Comment\n# Another comment\n\n", true, ""],
    ["", true, ""],
  ];

  for (const [input, newlineOk, expected] of cases) {
    it(`skips whitespace in ${JSON.stringify(input)} (newlineOk: ${newlineOk})`, () => {
      assert.equal(input.slice(parseSpace(input, 0, newlineOk)), expected);
    });
  }
});

describe("parseChar", () => {
  const simple: [string, string, number][] = [
    ["a simple char", "a", "a".codePointAt(0) as number],
    ["a digit", "9", "9".codePointAt(0) as number],
  ];

  for (const [description, char, codePoint] of simple) {
    it(`parses ${description}`, () => {
      const prefix = 'root ::= "';
      assert.deepEqual(parseChar(`${prefix}${char}" "foo"`, prefix.length), [codePoint, 1]);
    });
  }

  const escapes: [string, string, number, number][] = [
    ["escaped 8-bit unicode char", "\\x2A", "*".codePointAt(0) as number, 4],
    ["escaped 16-bit unicode char", "\\u006F", "o".codePointAt(0) as number, 6],
    ["escaped 32-bit unicode char", "\\U0001F4A9", 128169, 10],
    ["escaped tab char", "\\t", 9, 2],
    ["escaped new line char", "\\n", 10, 2],
    ["escaped carriage return char", "\\r", 13, 2],
    ["escaped quote char", '\\"', '"'.codePointAt(0) as number, 2],
    ["escaped [ char", "\\[", "[".codePointAt(0) as number, 2],
    ["escaped ] char", "\\]", "]".codePointAt(0) as number, 2],
    ["escaped \\ char", "\\\\", "\\".codePointAt(0) as number, 2],
  ];

  for (const [description, escapedChar, codePoint, incPos] of escapes) {
    it(`parses an ${description}`, () => {
      const prefix = 'root ::= "';
      assert.deepEqual(parseChar(`${prefix}${escapedChar}" "foo"`, prefix.length), [
        codePoint,
        incPos,
      ]);
    });
  }

  const raises: [string, number][] = [
    ["", 0],
    ["a", 1],
    ["a", 2],
  ];

  for (const [input, pos] of raises) {
    it(`throws for ${JSON.stringify(input)} at ${pos}`, () => {
      assert.throws(() => parseChar(input, pos), GrammarParseError);
    });
  }

  it("throws on an unknown escape", () => {
    assert.throws(() => parseChar('"\\q"', 1), {
      message: /Unknown escape at \\/,
    });
  });
});

describe("SymbolIds", () => {
  it("stores ids, positions and reverse lookups", () => {
    const symbolIds = new SymbolIds();
    symbolIds.set("root", 0, 4);
    symbolIds.set("foo", 1, 12);

    assert.equal(symbolIds.size, 2);
    assert.equal(symbolIds.get("root"), 0);
    assert.ok(symbolIds.has("foo"));
    assert.ok(!symbolIds.has("bar"));
    assert.deepEqual([...symbolIds.items()], [
      ["root", 0],
      ["foo", 1],
    ]);
    assert.equal(symbolIds.reverseGet(1), "foo");
    assert.equal(symbolIds.getPos("foo"), 12);
  });

  it("throws for unknown keys and values", () => {
    const symbolIds = new SymbolIds();
    assert.throws(() => symbolIds.reverseGet(3), {
      message: "SymbolIds does not contain value: 3",
    });
    assert.throws(() => symbolIds.getPos("nope"), {
      message: "SymbolIds does not contain key: nope",
    });
  });
});

describe("getOutElements", () => {
  it("builds the element matching the requested type", () => {
    assert.deepEqual(getOutElements(InternalRuleDefChar, 97), new InternalRuleDefChar([97]));
    assert.deepEqual(
      getOutElements(InternalRuleDefCharNot, 97),
      new InternalRuleDefCharNot([97]),
    );
    assert.deepEqual(
      getOutElements(InternalRuleDefCharRngUpper, 97),
      new InternalRuleDefCharRngUpper(97),
    );
    assert.deepEqual(getOutElements(InternalRuleDefAlt, 0), new InternalRuleDefAlt());
    assert.deepEqual(getOutElements(InternalRuleDefEnd, 0), new InternalRuleDefEnd());
    assert.deepEqual(
      getOutElements(InternalRuleDefCharAlt, 97),
      new InternalRuleDefCharAlt(97),
    );
  });

  it("throws for an unsupported type", () => {
    assert.throws(
      () => getOutElements(InternalRuleDefReference as never, 1),
      /Invalid type/,
    );
  });
});

describe("RulesBuilder", () => {
  it("parses a single string rule", () => {
    const parsed = new RulesBuilder('root ::= "foo"');
    assert.deepEqual(parsed.rules, [
      [
        new InternalRuleDefChar(["f".codePointAt(0) as number]),
        new InternalRuleDefChar(["o".codePointAt(0) as number]),
        new InternalRuleDefChar(["o".codePointAt(0) as number]),
        new InternalRuleDefEnd(),
      ],
    ]);
    assert.deepEqual([...parsed.symbolIds.items()], [["root", 0]]);
  });

  it("parses references between rules", () => {
    const parsed = new RulesBuilder('root ::= foo\n            foo ::= "bar"');
    assert.deepEqual([...parsed.symbolIds.items()], [
      ["root", 0],
      ["foo", 1],
    ]);
    assert.deepEqual(parsed.rules[0], [
      new InternalRuleDefReference(1),
      new InternalRuleDefEnd(),
    ]);
  });

  it("parses character ranges and alternates", () => {
    const parsed = new RulesBuilder("root  ::= [a-zA-Z0-9]");
    assert.deepEqual(parsed.rules, [
      [
        new InternalRuleDefChar(["a".codePointAt(0) as number]),
        new InternalRuleDefCharRngUpper("z".codePointAt(0) as number),
        new InternalRuleDefCharAlt("A".codePointAt(0) as number),
        new InternalRuleDefCharRngUpper("Z".codePointAt(0) as number),
        new InternalRuleDefCharAlt("0".codePointAt(0) as number),
        new InternalRuleDefCharRngUpper("9".codePointAt(0) as number),
        new InternalRuleDefEnd(),
      ],
    ]);
  });

  it("parses negations", () => {
    const parsed = new RulesBuilder("root ::= [^\\n]");
    assert.deepEqual(parsed.rules, [
      [new InternalRuleDefCharNot([10]), new InternalRuleDefEnd()],
    ]);
  });

  it("generates sub rules for modifiers", () => {
    const parsed = new RulesBuilder('root  ::= "f"*');
    assert.deepEqual([...parsed.symbolIds.items()], [
      ["root", 0],
      ["root_1", 1],
    ]);
    assert.deepEqual(parsed.rules[0], [
      new InternalRuleDefReference(1),
      new InternalRuleDefEnd(),
    ]);
    assert.deepEqual(parsed.rules[1], [
      new InternalRuleDefChar(["f".codePointAt(0) as number]),
      new InternalRuleDefReference(1),
      new InternalRuleDefAlt(),
      new InternalRuleDefEnd(),
    ]);
  });

  it("throws when a rule identifier is never defined", () => {
    assert.throws(() => new RulesBuilder("root ::= foo"), {
      message: /Undefined rule identifier "foo"/,
    });
  });

  it("throws when ::= is missing", () => {
    assert.throws(() => new RulesBuilder("root"), { message: /Expecting ::= at 4/ });
  });

  it("throws when a modifier has no preceding item", () => {
    assert.throws(() => new RulesBuilder("root ::= *"), {
      message: /Expecting preceding item to \*\/\+\/\? at 9/,
    });
  });

  it("throws when the time limit is exceeded", () => {
    assert.throws(() => new RulesBuilder('root ::= "foo"', -1), {
      message: /Duration of -1 exceeded/,
    });
  });
});
