// Runs the corpus through the reference implementation. Invoked by run.py.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const WORK = join(HERE, '.work');

const { default: GBNF } = await import(join(WORK, 'ref-src', 'index.ts'));

const cases = JSON.parse(readFileSync(join(WORK, 'corpus.json'), 'utf-8'));

const describeError = (err) => ({
  error: err?.name ?? 'Error',
  message: err?.message ?? String(err),
});

const rulesOf = (state) =>
  [...state].map((rule) =>
    rule.type === 'end' ? { type: rule.type } : { type: rule.type, value: rule.value },
  );

const results = cases.map(({ grammar, inputs }) => {
  const trace = { grammar, construct: null, adds: [] };
  let state;
  try {
    state = GBNF(grammar);
    trace.construct = { rules: rulesOf(state) };
  } catch (err) {
    trace.construct = describeError(err);
    return trace;
  }

  for (const input of inputs) {
    const entry = { input, whole: null, incremental: null };
    // the whole input applied to the state built above...
    try {
      entry.whole = { rules: rulesOf(state.add(input)) };
    } catch (err) {
      entry.whole = describeError(err);
    }
    // ...and the same input applied one character at a time to a fresh state
    try {
      let cursor = GBNF(grammar);
      for (const char of [...input]) {
        cursor = cursor.add(char);
      }
      entry.incremental = { rules: rulesOf(cursor) };
    } catch (err) {
      entry.incremental = describeError(err);
    }
    trace.adds.push(entry);
  }
  return trace;
});

writeFileSync(join(WORK, 'out-js.json'), JSON.stringify(results, null, 1));
console.log(`reference: wrote ${results.length} traces`);
