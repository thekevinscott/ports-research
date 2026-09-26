# GBNF

A library for parsing GBNF grammars, ported to TypeScript from the Python
reference implementation in `../reference_implementation`.

## Usage

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "foo"');
console.log([...state]); // [ RuleChar { value: [ 102 ], type: 'char' } ]

state = state.add('f');
console.log([...state]); // [ RuleChar { value: [ 111 ], type: 'char' } ]
```

`GBNF(grammar, initialString?)` returns a `ParseState`. A `ParseState` is
iterable, and yields the deduplicated set of rules (`RuleChar`,
`RuleCharExclude`, `RuleEnd`) that the grammar permits at the current position.
`ParseState.add(text)` returns a new `ParseState` advanced by `text`, and throws
an `InputParseError` if the text cannot be parsed. An invalid grammar throws a
`GrammarParseError`.

## Layout

The module layout mirrors the reference implementation:

| Python                            | TypeScript                       |
| --------------------------------- | -------------------------------- |
| `gbnf/GBNF.py`                     | `src/gbnf.ts`                    |
| `gbnf/rules_builder/`              | `src/rules-builder/`             |
| `gbnf/grammar_parser/`             | `src/grammar-parser/`            |
| `gbnf/grammar_graph/`              | `src/grammar-graph/`             |
| `gbnf/utils/`                      | `src/utils/`                     |

Differences worth noting:

- Python's `SymbolIds`/`Pointers` dict wrappers are backed by `Map`s, which
  preserve insertion order the same way Python dicts do.
- `RuleRef.nodes` is a `Set` of nodes in path order, so pointer resolution — and
  therefore the order rules are yielded in — is deterministic.
- Rules carry a `type` discriminator (`'char'`, `'char_exclude'`, `'end'`,
  `'ref'`) in place of Python's `isinstance` checks.
- Missing values are `undefined` rather than `None`; the Python code's
  `raise ValueError` becomes `throw new Error`.

## Tests

The generated suite from `/workspace/tests/javascript` is copied into `tests/`:

```sh
npx vitest run --config vitest.config.unit.ts
```
