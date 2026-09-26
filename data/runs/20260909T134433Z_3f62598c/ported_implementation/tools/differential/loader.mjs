import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const STUB = pathToFileURL(join(HERE, 'gbnf-rule-stub.ts')).href;

// The reference sources use ESM `.js` specifiers that actually point at `.ts`
// files, and import a `./builder/gbnf-rule.js` module that is not present in the
// checked in source tree. Map both so node can load the reference directly.
export async function resolve(specifier, context, nextResolve) {
  if (specifier.endsWith('builder/gbnf-rule.js')) {
    return { url: STUB, shortCircuit: true };
  }
  if (
    specifier.endsWith('.js') &&
    (specifier.startsWith('./') || specifier.startsWith('../'))
  ) {
    const resolved = new URL(specifier, context.parentURL);
    const asTs = new URL(resolved.href.replace(/\.js$/, '.ts'));
    if (!existsSync(fileURLToPath(resolved)) && existsSync(fileURLToPath(asTs))) {
      return { url: asTs.href, shortCircuit: true };
    }
  }
  return nextResolve(specifier, context);
}
