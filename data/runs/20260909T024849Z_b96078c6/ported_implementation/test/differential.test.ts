/**
 * Differential tests: every expectation in test/fixtures/reference.json was produced by
 * running the Python reference implementation (see scripts/generate_reference_fixture.py).
 * The port must agree with it exactly.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import { GBNF } from "../src/gbnf.ts";
import { buildRuleStack } from "../src/grammar-parser/build-rule-stack.ts";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../src/grammar-graph/grammar-graph-types.ts";
import type { UnresolvedRule } from "../src/grammar-graph/grammar-graph-types.ts";
import { RuleRef } from "../src/grammar-graph/rule-ref.ts";
import { RulesBuilder } from "../src/rules-builder/rules-builder.ts";
import type { InternalRuleDef } from "../src/rules-builder/rules-builder-types.ts";

interface SerializedRule {
  type: string;
  value?: unknown;
}

interface BuildFixture {
  key: string;
  grammar: string;
  error?: string;
  rules?: SerializedRule[][];
  symbolIds?: [string, number][];
  stacks?: SerializedRule[][][];
}

interface ParseStep {
  input: string | null;
  rules?: string[];
  error?: string;
}

interface InvalidFixture {
  key: string;
  grammar: string;
  errorType: string | null;
  error: string | null;
}

interface ParseFixture {
  key: string;
  grammar: string;
  inputs: string[];
  error?: string;
  steps: ParseStep[];
}

const fixture = JSON.parse(
  readFileSync(fileURLToPath(new URL("./fixtures/reference.json", import.meta.url)), "utf8"),
) as { build: BuildFixture[]; parse: ParseFixture[]; invalid: InvalidFixture[] };

/**
 * The reference implementation crashes with a raw `IndexError`/`KeyError` on these
 * grammars — it walks off the end of the string, or looks up a missing "root" key with
 * `symbol_ids["root"]` right after commenting that it expects `None` back. The port
 * raises the `GrammarParseError` the reference code clearly intends instead; see
 * PORTING-NOTES.md.
 */
const DIVERGENT_INVALID_GRAMMARS: Record<string, string> = {
  "unclosed group": "Expecting ')' at 13",
  "unterminated string": "Unexpected end of grammar input, failed to complete parse",
  "unterminated character class":
    "Unexpected end of grammar input, failed to complete parse",
  "missing root symbol": "Grammar does not contain a 'root' symbol",
};

const serializeInternal = (rule: InternalRuleDef): SerializedRule => {
  const name = rule.constructor.name;
  if ("value" in rule) {
    return { type: name, value: (rule as { value: unknown }).value };
  }
  return { type: name };
};

const serializeRule = (rule: UnresolvedRule): SerializedRule => {
  if (rule instanceof RuleEnd) {
    return { type: "RuleEnd" };
  }
  if (rule instanceof RuleChar) {
    return { type: "RuleChar", value: rule.value };
  }
  if (rule instanceof RuleCharExclude) {
    return { type: "RuleCharExclude", value: rule.value };
  }
  if (rule instanceof RuleRef) {
    return { type: "RuleRef", value: rule.value };
  }
  throw new Error(`unknown rule ${rule}`);
};

describe("differential: RulesBuilder + buildRuleStack", () => {
  for (const expected of fixture.build) {
    it(`matches the reference for ${expected.key}`, () => {
      if (expected.error !== undefined) {
        assert.throws(() => new RulesBuilder(expected.grammar), {
          message: expected.error,
        });
        return;
      }

      const builder = new RulesBuilder(expected.grammar);
      assert.deepEqual(
        builder.rules.map((rules) => rules.map(serializeInternal)),
        expected.rules,
      );
      assert.deepEqual([...builder.symbolIds.entries()], expected.symbolIds);
      assert.deepEqual(
        builder.rules.map((rules) =>
          buildRuleStack(rules).map((path) => path.map(serializeRule)),
        ),
        expected.stacks,
      );
    });
  }
});

describe("differential: GBNF parse states", () => {
  for (const [idx, expected] of fixture.parse.entries()) {
    it(`matches the reference for ${expected.key} #${idx}`, () => {
      // The fixture holds `json.dumps` output; re-encode both sides the same way so the
      // comparison (and the sort) is over identical representations.
      const normalize = (rules: string[]): string[] =>
        rules.map((rule) => JSON.stringify(JSON.parse(rule) as SerializedRule)).sort();
      const currentRules = (state: { [Symbol.iterator](): Iterator<UnresolvedRule> }) =>
        [...state].map((rule) => JSON.stringify(serializeRule(rule))).sort();

      if (expected.error !== undefined) {
        assert.throws(() => GBNF(expected.grammar), { message: expected.error });
        return;
      }

      let state = GBNF(expected.grammar);
      const [initial, ...steps] = expected.steps;
      assert.deepEqual(currentRules(state), normalize(initial.rules ?? []));

      for (const step of steps) {
        if (step.error !== undefined) {
          assert.throws(() => state.add(step.input as string), {
            message: step.error,
          });
          break;
        }
        state = state.add(step.input as string);
        assert.deepEqual(currentRules(state), normalize(step.rules ?? []));
      }
    });
  }
});

describe("differential: invalid grammars", () => {
  for (const expected of fixture.invalid) {
    it(`rejects ${expected.key}`, () => {
      const divergent = DIVERGENT_INVALID_GRAMMARS[expected.key];
      if (divergent !== undefined) {
        assert.throws(() => GBNF(expected.grammar), (err: Error) => {
          assert.equal(err.name, "GrammarParseError");
          assert.match(err.message, new RegExp(escapeRegExp(divergent)));
          return true;
        });
        return;
      }

      assert.equal(expected.errorType, "GrammarParseError");
      assert.throws(() => GBNF(expected.grammar), { message: expected.error as string });
    });
  }
});

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
