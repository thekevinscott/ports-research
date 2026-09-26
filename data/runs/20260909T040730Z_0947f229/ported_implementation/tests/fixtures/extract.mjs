// Extracts the `test.for([...])` case tables out of the generated JavaScript
// suite in /workspace/tests/javascript and writes them as JSON, so the Python
// tests exercise exactly the same cases rather than a hand-transcribed subset.
//
// Usage: node extract.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = '/workspace/tests/javascript';

const FILES = [
  'validation/validate-input.test.ts',
  'validation/validate-grammar.test.ts',
  'iteration/iteration.test.ts',
  'iteration/iteration-with-an-initial-string.test.ts',
  'iteration/iteration-with-additional-strings.test.ts',
  'iteration/grammars.test.ts',
];

// Scan forward from an opening `[` to its match, respecting string literals so
// that brackets inside grammar strings don't throw the count off.
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

const out = {};
for (const file of FILES) {
  const src = readFileSync(join(SRC, file), 'utf8');
  const tables = [];
  let from = 0;
  for (;;) {
    const marker = src.indexOf('test.for(', from);
    if (marker === -1) break;
    const open = src.indexOf('[', marker);
    const literal = readArrayLiteral(src, open);
    // eslint-disable-next-line no-eval
    tables.push(eval(literal));
    from = open + literal.length;
  }
  out[file] = tables;
}

writeFileSync(join(HERE, 'cases.json'), JSON.stringify(out, null, 1) + '\n');
for (const [file, tables] of Object.entries(out)) {
  console.log(file, tables.map((t) => t.length).join(', '));
}
