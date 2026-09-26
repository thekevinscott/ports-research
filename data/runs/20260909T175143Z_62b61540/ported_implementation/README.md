# GBNF

A TypeScript port of `reference_implementation/` (the Python `gbnf` package), a library for
parsing GBNF grammars.

## Usage

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "foo"');
state = state.add('f');
console.log([...state]); // [ RuleChar { type: 'char', value: [ 111 ] } ]
```

`GBNF(grammar, initialString?)` returns a `ParseState`. Iterating a `ParseState` yields the
set of rules (`RuleChar`, `RuleCharExclude`, `RuleEnd`) that may come next; `state.add(input)`
returns a new `ParseState` advanced by `input`, and throws an `InputParseError` if the input
cannot be parsed. An invalid grammar throws a `GrammarParseError`.

## Layout

Each module mirrors its counterpart in the Python reference:

| TypeScript | Python |
| --- | --- |
| `src/GBNF.ts` | `gbnf/GBNF.py` |
| `src/rules-builder/` | `gbnf/rules_builder/` |
| `src/grammar-parser/` | `gbnf/grammar_parser/` |
| `src/grammar-graph/` | `gbnf/grammar_graph/` |
| `src/utils/` | `gbnf/utils/` |

Two deliberate deviations, both on invalid-grammar error paths where the reference raises a
raw Python exception rather than its own error type:

- An unterminated `"` or `[` literal (e.g. `root ::= "foo`) raises `IndexError` in Python;
  here it throws the `GrammarParseError` that `parseChar` already defines for end of input.
  (Bounds-checking is also required in JS, where the out-of-range read would loop forever.)
- A grammar with no `root` symbol raises `KeyError` in Python; here it throws the
  `GrammarParseError` that `GBNF.py` defines but cannot reach.

The reference stores the nodes of a rule reference in an unordered Python `set`, so the order
in which it yields rules varies from run to run. This port uses an insertion-ordered `Set`,
which makes the yielded order deterministic and matches the test suite's expectations.

## Tests

```sh
npx vitest run --config vitest.config.unit.ts
```
