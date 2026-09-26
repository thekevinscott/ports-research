# gbnf (TypeScript)

A TypeScript port of `reference_implementation/gbnf`. Parse a GBNF grammar into a graph,
then walk it one code point at a time; at every step the parse state yields the rules that
could match next.

```ts
import GBNF, { InputParseError, RuleType } from './src/index';

let state = GBNF('root ::= "foo" | "bar"');
state = state.add('f');
[...state]; // [{ type: 'char', value: [111] }]
```

## Layout

Module-for-module with the reference implementation, with names converted to the JS
conventions (`snake_case` → `camelCase`, `snake_case.py` → `kebab-case.ts`):

| reference                          | port                                |
| ---------------------------------- | ----------------------------------- |
| `gbnf/rules_builder/`              | `src/rules-builder/` — grammar text → linear rule defs |
| `gbnf/grammar_parser/`             | `src/grammar-parser/` — linear rule defs → stacked rules |
| `gbnf/grammar_graph/`              | `src/grammar-graph/` — stacked rules → graph, pointers, parse state |
| `gbnf/utils/`                      | `src/utils/` — errors and range checks |

## Tests

The generated suite lives in `tests/`, per `tests/README.md`:

```sh
npx vitest run --config vitest.config.unit.ts
```

## Notes on fidelity

Two places where JavaScript's string model differs from Python's, and what the port does:

- `getInputAsCodePoints` iterates by code point (`Array.from`) rather than by UTF-16 unit,
  so astral characters in *input* match a single grammar char, as in the reference.
- The grammar parser itself (`src/rules-builder/`) indexes the grammar by UTF-16 unit,
  which is what the surrounding JS APIs expect. This only diverges from the reference for
  grammars containing astral characters, where a reported error column can differ.

`GBNF()`'s "does not contain a root symbol" message serializes the symbol list with
`JSON.stringify`, so it has no space after the commas that Python's `json.dumps` emits.
