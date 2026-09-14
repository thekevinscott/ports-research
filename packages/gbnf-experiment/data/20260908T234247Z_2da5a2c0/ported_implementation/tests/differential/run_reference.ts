// Runs the corpus through the TypeScript reference implementation and prints one
// JSON result per case to stdout. Invoked as:
//   node --experimental-transform-types run_reference.ts <reference-src-dir> <corpus.json>
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const [referenceDir, corpusPath] = process.argv.slice(2);
const { GBNF } = await import(resolve(referenceDir, 'gbnf.ts'));

type Case = {
  name: string;
  grammar: string;
  inputs?: string[];
  code_point_inputs?: (number | number[])[];
  steps?: string[];
};

const describeError = (e: any) => ({
  ok: false,
  error: e?.constructor?.name ?? 'Error',
  message: e?.message ?? String(e),
});

const describeState = (state: any) => ({
  ok: true,
  rules: [...state],
  size: state.size,
  grammar: state.grammar,
  graph: state._graph.print({ pointers: state._pointers, colors: false }),
  graphColored: state._graph.print({ pointers: state._pointers, colors: true }),
});

const corpus: Case[] = JSON.parse(readFileSync(corpusPath, 'utf8'));
const results: any[] = [];

for (const testCase of corpus) {
  const entry: any = { name: testCase.name };

  if (testCase.inputs !== undefined) {
    entry.inputs = testCase.inputs.map((input) => {
      try {
        return describeState(GBNF(testCase.grammar, input));
      } catch (e) {
        return describeError(e);
      }
    });
  }

  if (testCase.code_point_inputs !== undefined) {
    entry.code_point_inputs = testCase.code_point_inputs.map((input) => {
      try {
        return describeState(GBNF(testCase.grammar, input));
      } catch (e) {
        return describeError(e);
      }
    });
  }

  if (testCase.steps !== undefined) {
    const stepResults: any[] = [];
    try {
      let state = GBNF(testCase.grammar);
      stepResults.push(describeState(state));
      for (const step of testCase.steps) {
        try {
          state = state.add(step);
          stepResults.push(describeState(state));
        } catch (e) {
          stepResults.push(describeError(e));
          break;
        }
      }
    } catch (e) {
      stepResults.push(describeError(e));
    }
    entry.steps = stepResults;
  }

  results.push(entry);
}

console.log(JSON.stringify(results, null, 2));
