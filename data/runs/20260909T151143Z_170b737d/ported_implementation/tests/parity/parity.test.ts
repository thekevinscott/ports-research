/**
 * Differential test: replays the driver in `generate_fixtures.py` against the
 * TypeScript port and asserts every recorded value from the Python reference
 * still matches — rule tables, symbol ids, stacked rules, the rules exposed at
 * each parse step, the code points chosen from them, and error messages.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import { GBNF } from "../../src/index.ts";
import { build_rule_stack } from "../../src/grammar_parser/build_rule_stack.ts";
import { RulesBuilder } from "../../src/rules_builder/index.ts";
import type { ParseState } from "../../src/grammar_graph/parse_state.ts";

type Serialized = { t: string; v?: unknown };
type ErrorInfo = { type: string; message: string };
type Step = { rules: Serialized[]; cp?: number; error?: ErrorInfo };
type Walk = { error?: ErrorInfo; steps: Step[] };
type GrammarFixture = {
  grammar: string;
  builder_error?: ErrorInfo;
  stack_error?: ErrorInfo;
  rules?: Serialized[][];
  symbol_ids?: [string, number][];
  stacked_rules?: Serialized[][][];
  walk_first?: Walk;
  walk_last?: Walk;
};

const fixtures = JSON.parse(
  readFileSync(fileURLToPath(new URL("./fixtures.json", import.meta.url)), "utf8"),
) as { steps: number; grammars: GrammarFixture[]; invalid_grammars: GrammarFixture[] };

const serialize_value = (value: unknown): unknown =>
  Array.isArray(value) ? value.map(serialize_value) : value;

const serialize_obj = (obj: object): Serialized => {
  const entry: Serialized = { t: obj.constructor.name };
  const value = (obj as { value?: unknown }).value;
  if (value !== undefined && value !== null) {
    entry.v = serialize_value(value);
  }
  return entry;
};

const sort_key = (entry: Serialized): string =>
  JSON.stringify(Object.fromEntries(Object.entries(entry).sort(([a], [b]) => (a < b ? -1 : 1))));

// See the note in generate_fixtures.py: the reference's rule ordering depends on
// Python set iteration order, so both sides compare the sorted set of rules.
const serialize_rules = (state: ParseState): Serialized[] =>
  [...state]
    .map((rule) => serialize_obj(rule))
    .sort((a, b) => {
      const [ka, kb] = [sort_key(a), sort_key(b)];
      return ka < kb ? -1 : ka > kb ? 1 : 0;
    });

const describe_error = (error: unknown): ErrorInfo => {
  const err = error as Error;
  return { type: err.name, message: err.message };
};

const pick_code_point = (rules: Serialized[], prefer_last: boolean): number | null => {
  const candidates = prefer_last ? [...rules].reverse() : rules;
  for (const rule of candidates) {
    if (rule.t === "RuleChar") {
      const raw = rule.v as Array<number | [number, number]>;
      const values = prefer_last ? [...raw].reverse() : raw;
      const value = values[0];
      return Array.isArray(value) ? value[1] : value;
    }
    if (rule.t === "RuleCharExclude") {
      const excluded = rule.v as Array<number | [number, number]>;
      const span: number[] = [];
      if (prefer_last) {
        for (let c = 126; c > 31; c--) span.push(c);
      } else {
        for (let c = 32; c < 127; c++) span.push(c);
      }
      for (const candidate of span) {
        const hit = excluded.some((v) =>
          Array.isArray(v) ? v[0] <= candidate && candidate <= v[1] : v === candidate,
        );
        if (!hit) {
          return candidate;
        }
      }
    }
  }
  return null;
};

const walk = (grammar: string, prefer_last: boolean, max_steps: number): Walk => {
  const steps: Step[] = [];
  let state: ParseState;
  try {
    state = GBNF(grammar);
  } catch (error) {
    return { error: describe_error(error), steps };
  }

  for (let i = 0; i < max_steps; i++) {
    const rules = serialize_rules(state);
    const step: Step = { rules };
    steps.push(step);
    const code_point = pick_code_point(rules, prefer_last);
    if (code_point === null) {
      break;
    }
    step.cp = code_point;
    try {
      state = state.add(String.fromCodePoint(code_point));
    } catch (error) {
      step.error = describe_error(error);
      break;
    }
  }
  return { steps };
};

const label = (grammar: string): string => {
  const single_line = grammar.replace(/\s+/g, " ").trim();
  return single_line.length > 60 ? `${single_line.slice(0, 60)}…` : single_line || "(empty)";
};

const check_grammar = (fixture: GrammarFixture): void => {
  let builder: RulesBuilder | undefined;
  let builder_error: ErrorInfo | undefined;
  try {
    builder = new RulesBuilder(fixture.grammar);
  } catch (error) {
    builder_error = describe_error(error);
  }

  assert.deepStrictEqual(builder_error, fixture.builder_error, "RulesBuilder outcome");
  if (builder === undefined) {
    return;
  }

  assert.deepStrictEqual(
    builder.rules.map((rule) => rule.map(serialize_obj)),
    fixture.rules,
    "rules",
  );
  assert.deepStrictEqual([...builder.symbol_ids], fixture.symbol_ids, "symbol_ids");

  let stacked_rules: Serialized[][][] | undefined;
  let stack_error: ErrorInfo | undefined;
  try {
    stacked_rules = builder.rules.map((rule) =>
      build_rule_stack(rule).map((path) => path.map(serialize_obj)),
    );
  } catch (error) {
    stack_error = describe_error(error);
  }
  assert.deepStrictEqual(stack_error, fixture.stack_error, "build_rule_stack outcome");
  assert.deepStrictEqual(stacked_rules, fixture.stacked_rules, "stacked_rules");

  assert.deepStrictEqual(
    walk(fixture.grammar, false, fixtures.steps),
    fixture.walk_first,
    "walk picking the first accepted code point",
  );
  assert.deepStrictEqual(
    walk(fixture.grammar, true, fixtures.steps),
    fixture.walk_last,
    "walk picking the last accepted code point",
  );
};

describe("parity with the Python reference implementation", () => {
  describe("valid grammars", () => {
    for (const fixture of fixtures.grammars) {
      it(label(fixture.grammar), () => check_grammar(fixture));
    }
  });

  describe("invalid grammars", () => {
    for (const fixture of fixtures.invalid_grammars) {
      it(label(fixture.grammar), () => check_grammar(fixture));
    }
  });
});
