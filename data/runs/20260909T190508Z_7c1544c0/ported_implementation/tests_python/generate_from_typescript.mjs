/**
 * Extracts the data tables from the generated TypeScript suite in
 * `/workspace/tests/typescript` into JSON, so the Python tests in this
 * directory assert against exactly the same cases.
 *
 *   node tests_python/generate_from_typescript.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SUITE = process.env.GBNF_TEST_SUITE ?? '/workspace/tests/typescript';
const OUT = path.join(HERE, 'data');

/** Returns each `test.for([...])` array literal in a source file, evaluated. */
const extractTables = (source) => {
  const tables = [];
  const marker = 'test.for(';
  let searchFrom = 0;
  for (;;) {
    const start = source.indexOf(marker, searchFrom);
    if (start === -1) {
      break;
    }
    const open = source.indexOf('[', start);
    let depth = 0;
    let quote = null;
    let end = -1;
    for (let i = open; i < source.length; i++) {
      const char = source[i];
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
          end = i;
          break;
        }
      }
    }
    if (end === -1) {
      throw new Error('Unbalanced array literal in test file');
    }
    const literal = source.slice(open, end + 1);
    tables.push(new Function(`return ${literal};`)());
    searchFrom = end;
  }
  return tables;
};

const unescape = (str) => str.replace(/\\n/g, '\n').replace(/\\t/g, '\t');

const read = (relative) =>
  extractTables(fs.readFileSync(path.join(SUITE, relative), 'utf8'));

const [validGrammars, invalidGrammars] = read('validation/validate-grammar.test.ts');
const [validInputs, invalidInputs] = read('validation/validate-input.test.ts');
const [iteration] = read('iteration/iteration.test.ts');
const [initialString] = read('iteration/iteration-with-an-initial-string.test.ts');
const [throwingAdditionalStrings, additionalStrings] = read(
  'iteration/iteration-with-additional-strings.test.ts'
);
const [grammars] = read('iteration/grammars.test.ts');

const tables = {
  'valid-grammars': validGrammars,
  'invalid-grammars': invalidGrammars,
  'valid-inputs': validInputs,
  'invalid-inputs': invalidInputs,
  'iteration': iteration,
  'iteration-with-an-initial-string': initialString,
  'throwing-additional-strings': throwingAdditionalStrings,
  'iteration-with-additional-strings': additionalStrings,
  // the grammar files store their newlines escaped, exactly as the TS test unescapes them
  'grammars': grammars.map(([name, testCase, grammar]) => [
    name,
    unescape(testCase),
    unescape(grammar),
  ]),
};

fs.mkdirSync(OUT, { recursive: true });
for (const [name, table] of Object.entries(tables)) {
  fs.writeFileSync(path.join(OUT, `${name}.json`), `${JSON.stringify(table, null, 2)}\n`);
  console.log(`${name}.json: ${table.length} cases`);
}
