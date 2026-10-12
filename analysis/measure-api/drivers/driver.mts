// Steps one {grammar, input, chunks} case through the default export of the given entry and prints the steps.
import { readFileSync, writeSync } from "node:fs";
import { pathToFileURL } from "node:url";

const kase = JSON.parse(readFileSync(0, "utf-8"));
console.log = console.error;

const { default: GBNF } = await import(pathToFileURL(process.argv[2]).href);

function observe(label: string, call: () => any): [any, object] {
  try {
    const state = call();
    const rules = Array.from(state as Iterable<any>, (rule) => ({ type: rule?.type ?? null, value: rule?.value ?? null }));
    return [state, { step: label, rules }];
  } catch (e: any) {
    const pos = typeof e?.pos === "number" ? e.pos : null;
    return [null, { step: label, error: { class: e?.constructor?.name ?? typeof e, pos } }];
  }
}

const [start, first] = observe("construct", () => GBNF(kase.grammar));
const steps = [first];
if (start !== null) {
  steps.push(observe("whole", () => start.add(kase.input))[1]);
  let state = start;
  for (const [index, chunk] of (kase.chunks as string[]).entries()) {
    const [next, step] = observe(`prefix ${index + 1}`, () => state.add(chunk));
    steps.push(step);
    if (next === null) break;
    state = next;
  }
}

writeSync(1, JSON.stringify(steps));
