import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

// Not a package module: a subprocess entry point hyperfine shells out to via
// `pnpm dlx tsx`, mirroring run_vitest_suite's own host-subprocess execution
// strategy (src/index.ts as the port entry file, default-exporting GBNF)
// rather than inventing a second one.

function parseArg(name: string): string {
  const flag = `--${name}`;
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) {
    throw new Error(`missing required argument ${flag}`);
  }
  return process.argv[index + 1];
}

async function main(): Promise<void> {
  const target = parseArg("target");
  const grammarFile = parseArg("grammar-file");
  const iterations = Number.parseInt(parseArg("iterations"), 10);

  const entry = pathToFileURL(`${target}/src/index.ts`).href;
  const { default: GBNF } = await import(entry);
  const grammar = readFileSync(grammarFile, "utf-8");

  for (let i = 0; i < iterations; i++) {
    GBNF(grammar);
  }
}

main();
