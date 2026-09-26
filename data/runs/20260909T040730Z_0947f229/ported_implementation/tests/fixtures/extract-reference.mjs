// Extracts the case table from the reference implementation's own
// rules-builder unit test. That table pins the exact internal rule definitions
// the parser emits, which makes it the strongest available fidelity check on
// the port (the reference itself cannot be executed here — it has no installed
// dependencies and `src/gbnf.ts` imports a `./builder/gbnf-rule.js` module that
// is absent from the tree).
//
// Usage: node extract-reference.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = '/workspace/reference_implementation/src';

// Stands in for the enum the test file imports; every member's value is its name.
const InternalRuleType = Object.fromEntries(
  ['CHAR', 'CHAR_RNG_UPPER', 'RULE_REF', 'ALT', 'END', 'CHAR_NOT', 'CHAR_ALT'].map((k) => [k, k])
);

const readArrayLiteral = (src, start) => {
  let depth = 0;
  let quote = null;
  for (let i = start; i < src.length; i++) {
    const char = src[i];
    if (quote) {
      if (char === '\\') { i++; continue; }
      if (char === quote) quote = null;
      continue;
    }
    if (char === "'" || char === '"' || char === '`') { quote = char; continue; }
    if (char === '[') depth++;
    else if (char === ']') {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  throw new Error(`Unterminated array literal at ${start}`);
};

const file = 'rules-builder/rules-builder.test.ts';
const src = readFileSync(join(SRC, file), 'utf8');
const open = src.indexOf('[', src.indexOf('test.each('));
// One nested `as [...]` cast sits inside the table (on the escaped-char
// sub-table's `.map`); strip it so the literal is plain JavaScript.
const literal = readArrayLiteral(src, open).replace(/\s+as\s+\[[^)]*?\](?=\))/g, '');
// eslint-disable-next-line no-eval
const table = eval(`(function (InternalRuleType) { return ${literal}; })`)(InternalRuleType);

// The test file normalises each grammar before use: it collapses the indentation
// of the template literals to a literal `\n`, then expands that back to real
// newlines. Both halves are applied here so the Python test gets the final form.
const cases = table.map(([key, grammar, expectation]) => [
  key,
  grammar.split('\n').map((l) => l.trim()).join('\\n').split('\\n').join('\n'),
  expectation,
]);

writeFileSync(join(HERE, 'reference-cases.json'), JSON.stringify({ [file]: cases }, null, 1) + '\n');
console.log(file, cases.length);
