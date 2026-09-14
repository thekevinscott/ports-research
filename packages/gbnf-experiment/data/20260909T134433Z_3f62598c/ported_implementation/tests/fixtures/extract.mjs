// Extracts the `test.for([...])` data tables from the generated JavaScript test
// suite in /workspace/tests/javascript so the Python suite can run byte-identical
// cases. Usage: node tests/fixtures/extract.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SUITE = '/workspace/tests/javascript';

const FILES = [
  'validation/validate-grammar.test.ts',
  'validation/validate-input.test.ts',
  'iteration/iteration.test.ts',
  'iteration/iteration-with-an-initial-string.test.ts',
  'iteration/iteration-with-additional-strings.test.ts',
  'iteration/grammars.test.ts',
];

// Returns the index just past the array literal that starts at `start`, skipping
// over string literals so brackets inside strings don't confuse the matcher.
const findArrayEnd = (src, start) => {
  let depth = 0;
  let quote = null;
  for (let i = start; i < src.length; i++) {
    const char = src[i];
    if (quote) {
      if (char === '\\') {
        i++;
      } else if (char === quote) {
        quote = null;
      }
      continue;
    }
    if (char === "'" || char === '"' || char === '`') {
      quote = char;
    } else if (char === '[') {
      depth++;
    } else if (char === ']') {
      depth--;
      if (depth === 0) {
        return i + 1;
      }
    }
  }
  throw new Error('Unbalanced array literal');
};

for (const file of FILES) {
  const src = readFileSync(join(SUITE, file), 'utf-8');
  const blocks = [];
  let searchFrom = 0;
  for (;;) {
    const marker = src.indexOf('test.for(', searchFrom);
    if (marker === -1) {
      break;
    }
    const start = src.indexOf('[', marker);
    const end = findArrayEnd(src, start);
    // the captured text is a plain data literal
    blocks.push(eval(src.slice(start, end)));
    searchFrom = end;
  }
  const out = join(HERE, `${basename(file, '.test.ts')}.json`);
  writeFileSync(out, `${JSON.stringify(blocks, null, 2)}\n`);
  console.log(`${file} -> ${basename(out)} (${blocks.map(b => b.length).join(', ')} cases)`);
}
