# GBNF (TypeScript)

A TypeScript port of `reference_implementation/` (Python) — a library for parsing
`.gbnf` grammars and incrementally validating input against them.

## Usage

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "foo"');   // ParseState
state = state.add('f');               // throws InputParseError on invalid input
[...state];                           // [{ type: 'char', value: [111] }]
```

`GBNF(grammar, initialString?)` returns a `ParseState`. A `ParseState` is
immutable: `add()` returns a new state. Iterating a state yields the deduplicated
set of rules (`RuleChar`, `RuleCharExclude`, `RuleEnd`) that may come next.

Exports: `GBNF` (default and named), `GrammarParseError`, `InputParseError`,
`RuleChar`, `RuleCharExclude`, `RuleEnd`, `RuleType`, `ParseState`, `Graph`.

## Layout

The module layout mirrors the Python package (file names are kebab-cased):

| Python                         | TypeScript                        |
| ------------------------------ | --------------------------------- |
| `gbnf/GBNF.py`                 | `src/gbnf.ts`                     |
| `gbnf/rules_builder/`          | `src/rules-builder/`              |
| `gbnf/grammar_parser/`         | `src/grammar-parser/`             |
| `gbnf/grammar_graph/`          | `src/grammar-graph/`              |
| `gbnf/utils/`                  | `src/utils/`                      |

## Tests

The suite in `tests/` is a copy of `/workspace/tests/javascript`, per that
directory's README.

```sh
npx vitest run --config vitest.config.unit.ts
```

`node_modules/` holds symlinks to the globally installed `vitest` (this
environment has no npm registry access); recreate it with `npm i -D vitest` where
the registry is reachable.

## Deliberate differences from the Python reference

Both cases below are places where the Python reference crashes with an
unintended interpreter error; the port raises the library's own error instead,
consistent with the behaviour the JavaScript test suite expects elsewhere.

- A grammar with an unterminated group at end-of-input (`root ::= ([a-z]`) raises
  `GrammarParseError: Expecting ')' at 15` rather than Python's `IndexError`
  from indexing past the end of the source. The test suite asserts exactly this
  message for the same grammar when trailing text keeps the index in bounds.
- A grammar with no `root` symbol raises
  `GrammarParseError: Grammar does not contain a 'root' symbol` rather than
  Python's `KeyError: 'root'`. The Python check (`if symbol_ids["root"] is None`)
  can never be reached, since the lookup itself throws.

Rule iteration order also differs from the Python reference in some cases: the
Python `Graph` stores a rule reference's target nodes in a `set` (ordered by
object hash), whereas this port preserves insertion order, which is what the
JavaScript test suite asserts. Rule *contents* are identical in every case.
