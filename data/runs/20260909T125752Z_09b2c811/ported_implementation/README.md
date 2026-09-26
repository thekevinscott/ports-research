# GBNF (TypeScript)

A TypeScript port of `reference_implementation/` (the Python `gbnf` package): a library
for parsing `.gbnf` grammars and walking the resulting grammar graph.

## Usage

```ts
import GBNF, { InputParseError, GrammarParseError } from './src/index.js';

let state = GBNF('root ::= "foo"');
state = state.add('f');
console.log([...state]); // [ RuleChar { type: 'char', value: [ 111 ] } ]
```

`GBNF(grammar, initialString?)` returns a `ParseState`, which is iterable over the rules
that may come next (`RuleChar`, `RuleCharExclude`, `RuleEnd`), exposes `size` and
`grammar`, and returns a new `ParseState` from `add(text)`. Invalid grammars throw
`GrammarParseError`; input that the grammar cannot accept throws `InputParseError`.

## Layout

The module structure mirrors the Python package one-to-one (snake_case files become
kebab-case, snake_case functions become camelCase):

| Python | TypeScript |
| --- | --- |
| `gbnf/GBNF.py` | `src/GBNF.ts` |
| `gbnf/grammar_graph/` | `src/grammar-graph/` |
| `gbnf/grammar_parser/` | `src/grammar-parser/` |
| `gbnf/rules_builder/` | `src/rules-builder/` |
| `gbnf/utils/` | `src/utils/` |

## Tests

The generated suite from `tests/javascript` is copied into `tests/`:

```sh
vitest run --config vitest.config.unit.ts
```

## Deviations from the reference

These are the only behavioral differences, all in cases where the Python reference raises
an uncaught internal error or relies on unordered iteration:

- **Unterminated `"` strings and `[` char classes** (e.g. `root ::= "a`): Python raises a
  raw `IndexError` when indexing past the end of the grammar; the port raises the
  `GrammarParseError` ("Unexpected end of grammar input, failed to complete parse") that
  `parse_char` already defines, since reading past the end in JS would otherwise loop
  forever.
- **A grammar with no `root` symbol**: Python raises `KeyError('root')` before reaching
  its own check; the port raises the intended
  `GrammarParseError("Grammar does not contain a 'root' symbol")`.
- **Rule ordering**: `RuleRef.nodes` is a Python `set`, so the order in which alternate
  paths are yielded from a referenced rule is arbitrary (e.g. `root ::= [a-z]*` yields
  `end` before `char`). The port uses an insertion-ordered `Set`, so rules come out in
  grammar order (`char` then `end`), which is what the test suite expects.
