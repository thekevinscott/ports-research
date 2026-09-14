# gbnf (TypeScript)

A TypeScript port of `reference_implementation/` (the Python `gbnf` package).

```ts
import GBNF, { GrammarParseError, InputParseError, RuleType } from 'gbnf';

let state = GBNF('root ::= "foo"');
state = state.add('f');
[...state]; // [{ type: 'char', value: [111] }]
```

`GBNF(grammar, initialString?)` builds the grammar graph and returns a `ParseState`.
Iterating a `ParseState` yields the deduplicated set of rules that may match next
(`{ type: 'char' | 'char_exclude', value }` or `{ type: 'end' }`). `state.add(text)`
advances the parse and returns a new `ParseState`, throwing `InputParseError` when the
text cannot be matched; invalid grammars throw `GrammarParseError`.

## Layout

The module layout mirrors the reference implementation, with Python `snake_case`
filenames rendered as `kebab-case`:

| Python | TypeScript |
| --- | --- |
| `gbnf/GBNF.py` | `src/GBNF.ts` |
| `gbnf/__init__.py` | `src/index.ts` |
| `gbnf/grammar_graph/*` | `src/grammar-graph/*` |
| `gbnf/grammar_parser/*` | `src/grammar-parser/*` |
| `gbnf/rules_builder/*` | `src/rules-builder/*` |
| `gbnf/utils/*` | `src/utils/*` |

Notable translations:

- Rules are plain tagged objects (`{ type: RuleType.CHAR, value }`) rather than
  dataclasses; `RuleRef` stays a class because its `nodes` are patched in after the
  graph is built.
- Python's generators, `OrderedDict`, and `set` map to JS generators, `Map`, and `Set`,
  all of which preserve insertion order — which is what fixes the order rules are
  yielded in.
- Input is decoded to code points with `Array.from`, matching Python's per-code-point
  string iteration.

## Tests

```sh
npx vitest run --config vitest.config.unit.ts
```
