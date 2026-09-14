import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { GBNF } from "../src/GBNF.js";
import { getInputAsCodePoints } from "../src/grammar-graph/get-input-as-code-points.js";
import { getSerializedRuleKey } from "../src/grammar-graph/get-serialized-rule-key.js";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../src/grammar-graph/grammar-graph-types.js";
import { RuleRef } from "../src/grammar-graph/rule-ref.js";
import { isWordChar } from "../src/rules-builder/is-word-char.js";
import { parseChar } from "../src/rules-builder/parse-char.js";
import { parseName } from "../src/rules-builder/parse-name.js";
import { parseSpace } from "../src/rules-builder/parse-space.js";
import { SymbolIds } from "../src/rules-builder/symbol-ids.js";
import { buildErrorPosition } from "../src/utils/errors/build-error-position.js";
import { getInputAsString } from "../src/utils/errors/get-input-as-string.js";
import { GrammarParseError } from "../src/utils/errors/grammar-parse-error.js";
import { InputParseError } from "../src/utils/errors/input-parse-error.js";
import {
  IndexError,
  KeyError,
  ValueError,
} from "../src/utils/errors/python-errors.js";
import { isPointInRange } from "../src/utils/is-point-in-range.js";
import { validateNonEmpty } from "../src/utils/validate-non-empty.js";
import type { Range, ValidInput } from "../src/grammar-graph/grammar-graph-types.js";

const helpers: {
  helpers: {
    errorPositions: {
      src: string;
      pos: number;
      lines: string[] | null;
      error?: { type: string; message: string };
    }[];
    inputs: {
      input: ValidInput;
      asString: string;
      asCodePoints: number[];
    }[];
    pointRanges: { point: number; range: Range; result: boolean }[];
  };
} = JSON.parse(
  readFileSync(
    fileURLToPath(new URL("./fixtures/fixtures.json", import.meta.url)),
    "utf8",
  ),
);

describe("buildErrorPosition", () => {
  for (const { src, pos, lines, error } of helpers.helpers.errorPositions) {
    it(`matches the reference for ${JSON.stringify(src)} at ${pos}`, () => {
      if (error) {
        expect(() => buildErrorPosition(src, pos)).toThrowError(
          expect.objectContaining({
            name: error.type,
            message: error.message,
          }),
        );
        return;
      }
      expect(buildErrorPosition(src, pos)).toEqual(lines);
    });
  }
});

describe("input conversion", () => {
  for (const { input, asString, asCodePoints } of helpers.helpers.inputs) {
    it(`converts ${JSON.stringify(input)}`, () => {
      expect(getInputAsString(input)).toBe(asString);
      expect(getInputAsCodePoints(input)).toEqual(asCodePoints);
    });
  }

  it("rejects non integer code points", () => {
    expect(() => getInputAsCodePoints([1.5])).toThrowError(ValueError);
  });
});

describe("isPointInRange", () => {
  for (const { point, range, result } of helpers.helpers.pointRanges) {
    it(`${point} in [${range.join(", ")}] is ${result}`, () => {
      expect(isPointInRange(point, range)).toBe(result);
    });
  }

  it("rejects non integer points", () => {
    expect(() => isPointInRange(1.5, [0, 5])).toThrowError(ValueError);
  });
});

describe("validateNonEmpty", () => {
  it("returns the value", () => {
    expect(validateNonEmpty([1, 2])).toEqual([1, 2]);
  });

  it("throws on an empty value", () => {
    expect(() => validateNonEmpty([])).toThrowError(
      new ValueError("Value cannot be empty."),
    );
  });
});

describe("isWordChar", () => {
  it.each<[string, boolean]>([
    ["a", true],
    ["Z", true],
    ["-", false],
    ["_", false],
    ["0", false],
    [" ", false],
  ])("%s -> %s", (char, expected) => {
    expect(isWordChar(char)).toBe(expected);
  });
});

describe("parseSpace", () => {
  it("skips spaces and tabs", () => {
    expect(parseSpace("  \t a", 0, false)).toBe(4);
  });

  it("stops at a newline when newlines are not ok", () => {
    expect(parseSpace("  \n  a", 0, false)).toBe(2);
  });

  it("skips newlines when newlines are ok", () => {
    expect(parseSpace("  \n  a", 0, true)).toBe(5);
  });

  it("skips comments up to the end of the line", () => {
    expect(parseSpace("# comment\nx", 0, false)).toBe(9);
    expect(parseSpace("# comment\nx", 0, true)).toBe(10);
  });

  it("handles the end of the input", () => {
    expect(parseSpace("   ", 0, true)).toBe(3);
    expect(parseSpace("", 0, true)).toBe(0);
  });
});

describe("parseName", () => {
  it("reads word characters and separators", () => {
    expect(parseName("my-rule_name ::= x", 0)).toBe("my-rule_name");
  });

  it("stops at the first invalid character", () => {
    expect(parseName("abc123", 0)).toBe("abc");
  });

  it("throws when no name is found", () => {
    expect(() => parseName("::= x", 0)).toThrowError(
      new GrammarParseError("::= x", 0, "Failed to find a valid name"),
    );
  });
});

describe("parseChar", () => {
  it.each<[string, [number, number]]>([
    ["a", [97, 1]],
    ["\\n", [10, 2]],
    ["\\t", [9, 2]],
    ["\\r", [13, 2]],
    ['\\"', [34, 2]],
    ["\\[", [91, 2]],
    ["\\]", [93, 2]],
    ["\\\\", [92, 2]],
    ["\\x41", [65, 4]],
    ["\\u00e9", [233, 6]],
    ["\\U0001F600", [128512, 10]],
  ])("parses %s", (src, expected) => {
    expect(parseChar(src, 0)).toEqual(expected);
  });

  it("throws past the end of the input", () => {
    expect(() => parseChar("ab", 2)).toThrowError(
      new GrammarParseError(
        "ab",
        2,
        "Unexpected end of grammar input, failed to complete parse",
      ),
    );
  });

  it("throws on an unknown escape", () => {
    expect(() => parseChar("\\q", 0)).toThrowError(
      new GrammarParseError("\\q", 0, "Unknown escape at \\"),
    );
  });

  it("throws on an invalid hex escape", () => {
    expect(() => parseChar("\\xzz", 0)).toThrowError(ValueError);
  });
});

describe("SymbolIds", () => {
  it("stores ids, positions, and the reverse mapping", () => {
    const symbolIds = new SymbolIds();
    symbolIds.set("root", 0, 4);
    symbolIds.set("expr", 1, 20);

    expect(symbolIds.size).toBe(2);
    expect(symbolIds.get("root")).toBe(0);
    expect(symbolIds.has("expr")).toBe(true);
    expect(symbolIds.has("nope")).toBe(false);
    expect(symbolIds.reverseGet(1)).toBe("expr");
    expect(symbolIds.getPos("expr")).toBe(20);
    expect([...symbolIds]).toEqual([
      ["root", 0],
      ["expr", 1],
    ]);
  });

  it("throws like Python's dict lookup for a missing key", () => {
    const symbolIds = new SymbolIds();
    expect(() => symbolIds.get("root")).toThrowError(new KeyError("root"));
    expect(() => symbolIds.reverseGet(3)).toThrowError(
      new ValueError("SymbolIds does not contain value: 3"),
    );
    expect(() => symbolIds.getPos("root")).toThrowError(
      new ValueError("SymbolIds does not contain key: root"),
    );
  });
});

describe("getSerializedRuleKey", () => {
  it("serializes each rule type the way the reference does", () => {
    expect(getSerializedRuleKey(new RuleEnd())).toBe("0");
    expect(getSerializedRuleKey(new RuleChar([97, [98, 122]]))).toBe(
      "1-[97, [98, 122]]",
    );
    expect(getSerializedRuleKey(new RuleCharExclude([97]))).toBe("2-[97]");
    expect(getSerializedRuleKey(new RuleRef(7))).toBe("3-7");
  });
});

describe("rules", () => {
  it("compares by value, and copies the incoming list", () => {
    const value: (number | Range)[] = [97];
    const rule = new RuleChar(value);
    value.push(98);

    expect(rule.value).toEqual([97]);
    expect(rule.equals(new RuleChar([97]))).toBe(true);
    expect(rule.equals(new RuleChar([98]))).toBe(false);
    expect(rule.equals(new RuleCharExclude([97]))).toBe(false);
    expect(new RuleEnd().equals(new RuleEnd())).toBe(true);
    expect(new RuleRef(1).equals(new RuleRef(1))).toBe(true);
    expect(new RuleRef(1).equals(new RuleRef(2))).toBe(false);
  });

  it("reports its type and dict the way the reference does", () => {
    expect(new RuleEnd().toDict()).toEqual({ type: "RuleEnd" });
    expect(new RuleChar([97]).toDict()).toEqual({
      type: "RuleChar",
      value: [97],
    });
    expect(String(new RuleChar([[97, 122], 98]))).toBe(
      "RuleChar(value=[[97, 122], 98])",
    );
    expect(String(new RuleEnd())).toBe("RuleEnd()");
  });

  it("throws when a rule ref's nodes have not been set", () => {
    expect(() => new RuleRef(1).nodes).toThrowError(
      new ValueError("Nodes are not set"),
    );
  });
});

describe("errors", () => {
  it("exposes the grammar, position, and reason", () => {
    const error = new GrammarParseError('root ::= "a"', 9, "boom");
    expect(error.grammar).toBe('root ::= "a"');
    expect(error.pos).toBe(9);
    expect(error.reason).toBe("boom");
    expect(error.toString()).toBe(
      ['Failed to parse grammar: boom', "", 'root ::= "a"', "         ^"].join(
        "\n",
      ),
    );
    expect(error.message).toBe(error.toString());
    expect(error.equals(error.toString())).toBe(true);
  });

  it("positions input errors relative to the previous input", () => {
    const error = new InputParseError([97, 98, 99], 1, "xy");
    expect(error.src).toBe("xyabc");
    expect(error.pos).toBe(1);
    expect(error.toString()).toBe(
      ["Failed to parse input string:", "", "xyabc", "   ^"].join("\n"),
    );
    expect(error.errorForMostRecentInput).toBe(
      ["Failed to parse input string:", "", "abc", " ^"].join("\n"),
    );
  });

  it("defaults the previous input to an empty string", () => {
    const error = new InputParseError("abc", 2);
    expect(error.src).toBe("abc");
    expect(error.toString()).toBe(error.errorForMostRecentInput);
  });
});

describe("GBNF", () => {
  it("rejects non string arguments", () => {
    expect(() => GBNF(1 as unknown as string)).toThrowError(
      new ValueError("grammar must be a string"),
    );
    expect(() => GBNF("root ::= \"a\"", 1 as unknown as string)).toThrowError(
      new ValueError("input must be a string"),
    );
    expect(() => GBNF('root ::= "a"').add(1 as unknown as string)).toThrowError(
      new ValueError("input text must be of type string"),
    );
  });

  it("raises a KeyError for a grammar without a root rule", () => {
    expect(() => GBNF('foo ::= "a"')).toThrowError(new KeyError("root"));
  });

  it("raises for a grammar with no rules", () => {
    expect(() => GBNF("")).toThrowError(
      new GrammarParseError("", 0, "No rules were found"),
    );
  });

  it("raises an IndexError for an unterminated string, like the reference", () => {
    expect(() => GBNF('root ::= "a')).toThrowError(IndexError);
  });

  it("exposes the grammar, size, and rules", () => {
    const grammar = 'root ::= "a" | [x-z]';
    const state = GBNF(grammar);
    expect(state.grammar).toBe(grammar);
    expect(state.size).toBe(2);
    expect([...state].map((rule) => rule.toDict())).toEqual([
      { type: "RuleChar", value: [97] },
      { type: "RuleChar", value: [[120, 122]] },
    ]);
  });

  it("returns a new state on add, leaving the previous state usable", () => {
    const state = GBNF('root ::= "abc"');
    const next = state.add("a");
    expect(next).not.toBe(state);
    expect([...state].map((rule) => rule.toDict())).toEqual([
      { type: "RuleChar", value: [97] },
    ]);
    expect([...next].map((rule) => rule.toDict())).toEqual([
      { type: "RuleChar", value: [98] },
    ]);
    expect([...next.add("b").add("c")].map((rule) => rule.toDict())).toEqual([
      { type: "RuleEnd" },
    ]);
  });

  it("accepts an initial string", () => {
    expect([...GBNF('root ::= "abc"', "ab")].map((rule) => rule.toDict())).toEqual(
      [{ type: "RuleChar", value: [99] }],
    );
  });

  it("reports where the input stopped matching", () => {
    const state = GBNF('root ::= "abc"', "a");
    let error: unknown;
    try {
      state.add("x");
    } catch (err) {
      error = err;
    }
    expect(error).toBeInstanceOf(InputParseError);
    expect((error as InputParseError).toString()).toBe(
      ["Failed to parse input string:", "", "ax", " ^"].join("\n"),
    );
  });
});

describe("graph printing", () => {
  it("prints every path of the graph", () => {
    const state = GBNF('root ::= "a" | [x-z]');
    expect(state.graph.print()).toBe(
      ["{0,0,0}[a]-> {0,0,1}RuleEnd", "{0,1,0}[xz]-> {0,1,1}RuleEnd"].join("\n"),
    );
  });

  it("marks the active pointers", () => {
    const state = GBNF('root ::= "ab"');
    expect(state.graph.print(state.pointers)).toBe(
      "{0,0,0}[a][*]-> {0,0,1}[b]-> {0,0,2}RuleEnd",
    );
  });

  it("can colorize its output", () => {
    const state = GBNF('root ::= "a"');
    expect(state.graph.print(null, true)).toContain("\x1b[33m");
  });
});
