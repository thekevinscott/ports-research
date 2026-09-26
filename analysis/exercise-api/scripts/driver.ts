import { readFileSync, writeSync } from "node:fs";
import { pathToFileURL } from "node:url";

// Not a package module: a subprocess entry point run_driver shells out to via
// `pnpm dlx tsx`, loading `<target>/src/index.ts` the way run_vitest_suite's alias
// does. `--adapt` applies that package's default_export rule.

const TYPE_NAMES: Record<string, string> = {
  rulechar: "char",
  char: "char",
  rulecharexclude: "char_exclude",
  charexclude: "char_exclude",
  char_exclude: "char_exclude",
  ruleend: "end",
  end: "end",
};

type Result = {
  ok: boolean;
  error_type: string | null;
  error_pos: number | null;
  rules: unknown[] | null;
  elapsed_ns: number | null;
  construct_ns: number | null;
  add_ns: number | null;
};

const LOAD_ERROR = { ok: false, error_type: "LoadError", error_pos: null, rules: null, elapsed_ns: null };

function parseArg(name: string): string {
  const index = process.argv.indexOf(`--${name}`);
  if (index === -1 || index + 1 >= process.argv.length) {
    throw new Error(`missing required argument --${name}`);
  }
  return process.argv[index + 1];
}

function parseCount(name: string, fallback: number): number {
  const index = process.argv.indexOf(`--${name}`);
  return index === -1 ? fallback : Number(process.argv[index + 1]);
}

function normalizeType(raw: unknown): string {
  const name = String(raw).toLowerCase().replace(/-/g, "_").replace(/^ruletype\./, "");
  return TYPE_NAMES[name] ?? TYPE_NAMES[name.replace(/_/g, "")] ?? name;
}

function normalizeRule(rule: any): Record<string, unknown> {
  const rawType = rule?.type ?? rule?.constructor?.name;
  const normalized: Record<string, unknown> = { type: normalizeType(rawType) };
  if (rule !== null && typeof rule === "object" && "value" in rule) {
    normalized.value = rule.value;
  }
  return normalized;
}

function runCase(GBNF: any, grammar: string, input: string): Result {
  const start = process.hrtime.bigint();
  try {
    const parser = GBNF(grammar);
    const constructed = process.hrtime.bigint();
    const state = parser.add(input);
    const added = process.hrtime.bigint();
    const rules = Array.from(state as Iterable<unknown>, normalizeRule);
    return {
      ok: true,
      error_type: null,
      error_pos: null,
      rules,
      elapsed_ns: Number(process.hrtime.bigint() - start),
      construct_ns: Number(constructed - start),
      add_ns: Number(added - constructed),
    };
  } catch (e: any) {
    const pos = e?.pos;
    return {
      ok: false,
      error_type: e?.constructor?.name ?? e?.name ?? String(e),
      error_pos: typeof pos === "number" ? pos : null,
      rules: null,
      elapsed_ns: Number(process.hrtime.bigint() - start),
      construct_ns: null,
      add_ns: null,
    };
  }
}

async function load(target: string, adapt: boolean): Promise<any> {
  const mod = await import(pathToFileURL(`${target}/src/index.ts`).href);
  let GBNF = mod.default;
  if (adapt && GBNF === undefined && "GBNF" in mod) {
    GBNF = mod.GBNF;
  }
  if (typeof GBNF !== "function") {
    throw new Error("no GBNF entry point");
  }
  return GBNF;
}

function write(record: unknown): void {
  writeSync(1, JSON.stringify(record, (_, v) => (typeof v === "bigint" ? Number(v) : v)) + "\n");
}

async function main(): Promise<void> {
  const target = parseArg("target");
  const adapt = process.argv.includes("--adapt");
  const repeat = parseCount("repeat", 1);
  const warmup = parseCount("warmup", 0);
  console.log = console.error;
  const cases = readFileSync(0, "utf-8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));

  let GBNF: any = null;
  try {
    GBNF = await load(target, adapt);
  } catch {
    GBNF = null;
  }
  if (GBNF === null) {
    for (const _ of cases) write(LOAD_ERROR);
    return;
  }

  // A case may carry its own budget: the timeout covers the whole list, so without one
  // the slowest case dictates how often every other case can be measured.
  const budgets = cases.map((c) => ({
    warmup: c.warmup ?? warmup,
    repeat: Math.max(c.repeat ?? repeat, 1),
  }));
  const samples = cases.map(() => ({ construct_ns: [] as (number | null)[], add_ns: [] as (number | null)[] }));
  const results: Record<string, unknown>[] = cases.map(() => ({}));
  const passes = Math.max(0, ...budgets.map((b) => b.warmup + b.repeat));
  for (let pass = 0; pass < passes; pass++) {
    for (let index = 0; index < cases.length; index++) {
      if (pass >= budgets[index].warmup + budgets[index].repeat) continue;
      const { construct_ns, add_ns, ...rest } = runCase(GBNF, cases[index].grammar, cases[index].input);
      if (pass >= budgets[index].warmup) {
        samples[index].construct_ns.push(construct_ns);
        samples[index].add_ns.push(add_ns);
      }
      results[index] = rest;
    }
  }
  for (let index = 0; index < cases.length; index++) {
    const keep = repeat > 1 || "repeat" in cases[index];
    write(keep ? { ...results[index], ...samples[index] } : results[index]);
  }
}

main();
