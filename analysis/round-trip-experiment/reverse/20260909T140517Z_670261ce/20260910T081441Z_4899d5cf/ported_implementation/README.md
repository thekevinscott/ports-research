# gbnf (TypeScript port)

A TypeScript port of `reference_implementation/` — the Python `gbnf` library for
parsing GBNF grammars.

## Usage

```ts
import GBNF from 'gbnf';

const state = GBNF('root ::= "yes" | "no"');
for (const rule of state) {
  console.log(rule);
  // { type: 'char', value: [121] }   // "y"
  // { type: 'char', value: [110] }   // "n"
}
```

If the grammar is invalid, `GBNF` throws a `GrammarParseError`.

`state` is iterable (`[...state]`) and can also be iterated through `state.rules()`.
States are *immutable*; to parse more input call `state.add()`, which returns a new
state:

```ts
let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]);   // [{ type: 'char', value: [73] }]    // "I"
state = state.add('I li');
console.log([...state]);   // [{ type: 'char', value: [107] }]   // "k"
state = state.add('ke gree');
console.log([...state]);   // [{ type: 'char', value: [110] }]   // "n"
```

Input that the grammar cannot accept throws an `InputParseError`.

The rules returned are plain objects:

- `RuleChar` — `{ type: 'char', value }`, where `value` holds code points to match
  and an entry may itself be a `[start, end]` range.
- `RuleCharExclude` — `{ type: 'char_exclude', value }`, the same, for code points
  that must *not* match.
- `RuleEnd` — `{ type: 'end' }`, a valid end of the string.

`ValidInput` — accepted by `GBNF`'s second argument and by `state.add()` — is a
string, a single code point, or an array of code points.

## Layout

The module layout mirrors the reference one-to-one, so the two can be read side by
side:

| reference (Python)                | port (`src/`)                     |
| --------------------------------- | --------------------------------- |
| `gbnf.py`                         | `gbnf.ts`                         |
| `rules_builder/*.py`              | `rules-builder/*.ts`              |
| `grammar_parser/build_rule_stack` | `grammar-parser/build-rule-stack` |
| `grammar_graph/*.py`              | `grammar-graph/*.ts`              |
| `utils/**/*.py`                   | `utils/**/*.ts`                   |

Names are camelCased. The reference's camelCase aliases (`isRange` alongside
`is_range`) collapse back into the single camelCase spelling.

## Tests

```bash
cp -r /workspace/tests/typescript tests
cp tests/vitest.config.unit.ts .
vitest run --config vitest.config.unit.ts
```

`vitest.config.unit.ts` aliases `gbnf` to `src/index.ts`.

Beyond that suite, the port was checked against the corpus the reference itself is
pinned to: all 258 cases in `reference_implementation/tests/fixtures/reference.json`
(recorded from the original Javascript) match exactly, as do 1946 seeded random
grammar/input pairs replayed through the Python reference, comparing every
intermediate rule set, `size`, `grammar`, and error message.

## Notes on the port

The reference's three deliberate deviations from the original Javascript are kept,
since they are equally correct here:

1. **Non-BMP characters.** The original Javascript indexes strings as UTF-16, so it
   splits characters above `U+FFFF` into surrogate halves. Grammars are carried
   through this port as arrays of code points (`utils/js.ts`'s `Chars`), so
   `GBNF('root ::= "😀"')` matches the whole character and `\U0001F600` matches `😀`
   as input.
2. **Infinite recursion.** A grammar that can expand forever (`root ::= a*` with
   `a ::= "b"?`, or `root ::= root`) makes the original exhaust the call stack. The
   graph is walked iteratively here, so an explicit depth bound
   (`grammar-graph/graph-pointer.ts`'s `MAX_POINTER_DEPTH`) raises a `RangeError`
   instead — the same error type a stack overflow produces, at a bound far above
   what real grammars use. A chain of 2000 rule references still parses.
3. **Missing `root` symbol.** `SymbolIds.get` throws on a missing key, which in the
   original masked the intended error; the port checks `symbolIds.has('root')` first
   and throws the `GrammarParseError` that names the symbols the grammar does define.

Two smaller notes:

- The original's `src/builder/` is not part of the reference snapshot, so the
  builder API is not ported. `GBNF()` accepts a string, or any value whose
  `String()` is the grammar.
- An invalid hex escape (`"\x"` with no digits) yields `NaN` in the original, which
  silently matches nothing. Both the reference and this port throw a
  `GrammarParseError`.

Imports use `.js` specifiers (the NodeNext convention the original Javascript source
used), so `src/` loads both through a bundler and directly under Node's TypeScript
support.
