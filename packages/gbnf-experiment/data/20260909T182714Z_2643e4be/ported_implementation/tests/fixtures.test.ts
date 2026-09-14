import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { GBNF } from "../src/GBNF.js";
import type { ResolvedRule } from "../src/grammar-graph/grammar-graph-types.js";
import { buildRuleStack } from "../src/grammar-parser/build-rule-stack.js";
import { RulesBuilder } from "../src/rules-builder/rules-builder.js";

interface SerializedError {
  type: string;
  message: string;
}

interface Step {
  input: string;
  rules: Record<string, unknown>[];
}

interface Sequence {
  inputs: string[];
  steps: Step[];
  error?: SerializedError;
}

interface Case {
  name: string;
  grammar: string;
  sequences: Sequence[];
  internalRules: Record<string, unknown>[][] | null;
  symbolIds: Record<string, number> | null;
  builderError?: SerializedError;
  stackedRules?: Record<string, unknown>[][][] | null;
  stackError?: SerializedError;
}

const fixtures: { cases: Case[] } = JSON.parse(
  readFileSync(
    fileURLToPath(new URL("./fixtures/fixtures.json", import.meta.url)),
    "utf8",
  ),
);

const serializeError = (err: unknown): SerializedError => {
  if (!(err instanceof Error)) {
    throw err;
  }
  return { type: err.name, message: err.message };
};

const captureError = (fn: () => void): SerializedError | null => {
  try {
    fn();
  } catch (err) {
    return serializeError(err);
  }
  return null;
};

const serializeInternalRule = (rule: object): Record<string, unknown> => {
  const out: Record<string, unknown> = { type: rule.constructor.name };
  if ("value" in rule) {
    out.value = (rule as { value: unknown }).value;
  }
  return out;
};

const canonical = (value: unknown): string =>
  JSON.stringify(value, (_key, val: unknown) => {
    if (val && typeof val === "object" && !Array.isArray(val)) {
      return Object.fromEntries(
        Object.entries(val as Record<string, unknown>).sort(([a], [b]) =>
          a < b ? -1 : a > b ? 1 : 0,
        ),
      );
    }
    return val;
  });

const sortedRules = (rules: Iterable<ResolvedRule>): Record<string, unknown>[] =>
  [...rules]
    .map((rule) => rule.toDict())
    .sort((a, b) => {
      const [x, y] = [canonical(a), canonical(b)];
      return x < y ? -1 : x > y ? 1 : 0;
    });

describe("differential fixtures from the reference implementation", () => {
  for (const testCase of fixtures.cases) {
    describe(testCase.name, () => {
      it("builds the same internal rules", () => {
        let builder: RulesBuilder | undefined;
        const error = captureError(() => {
          builder = new RulesBuilder(testCase.grammar);
        });

        if (testCase.builderError) {
          expect(error).toEqual(testCase.builderError);
          return;
        }

        expect(error).toBeNull();
        expect(
          builder!.rules.map((rules) => rules.map(serializeInternalRule)),
        ).toEqual(testCase.internalRules);
        expect(Object.fromEntries(builder!.symbolIds.items())).toEqual(
          testCase.symbolIds,
        );
      });

      if (testCase.internalRules !== null) {
        it("builds the same rule stacks", () => {
          const builder = new RulesBuilder(testCase.grammar);
          let stacked: Record<string, unknown>[][][] | undefined;
          const error = captureError(() => {
            stacked = builder.rules.map((rules) =>
              buildRuleStack(rules).map((path) =>
                path.map((rule) =>
                  "toDict" in rule
                    ? rule.toDict()
                    : { type: "RuleRef", value: rule.value },
                ),
              ),
            );
          });

          if (testCase.stackError) {
            expect(error).toEqual(testCase.stackError);
            return;
          }

          expect(error).toBeNull();
          expect(stacked).toEqual(testCase.stackedRules);
        });
      }

      for (const [index, sequence] of testCase.sequences.entries()) {
        it(`parses input sequence ${index}: ${JSON.stringify(sequence.inputs)}`, () => {
          const steps: Step[] = [];
          const error = captureError(() => {
            let state = GBNF(testCase.grammar, sequence.inputs[0]);
            steps.push({
              input: sequence.inputs[0],
              rules: sortedRules(state),
            });
            for (const chunk of sequence.inputs.slice(1)) {
              state = state.add(chunk);
              steps.push({ input: chunk, rules: sortedRules(state) });
            }
          });

          expect(steps).toEqual(sequence.steps);
          expect(error).toEqual(sequence.error ?? null);
        });
      }
    });
  }
});
