// Runs one {grammar, input} pair through the default export of the given entry and prints {outcome, error}.
import { readFileSync, writeSync } from "node:fs";
import { pathToFileURL } from "node:url";

const pair = JSON.parse(readFileSync(0, "utf-8"));
console.log = console.error;

const { default: GBNF } = await import(pathToFileURL(process.argv[2]).href);

let outcome: string;
let error: string | null = null;
try {
  const state = GBNF(pair.grammar, pair.input);
  outcome = Array.from(state as Iterable<{ type: string }>).some((rule) => rule.type === "end") ? "accept" : "reject";
} catch (e: any) {
  const name = e?.constructor?.name ?? typeof e;
  outcome = name === "InputParseError" ? "reject" : "error";
  error = `${name}: ${e?.message ?? String(e)}`;
}

writeSync(1, JSON.stringify({ outcome, error }));
