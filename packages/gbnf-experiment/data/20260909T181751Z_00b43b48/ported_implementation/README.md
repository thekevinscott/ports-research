# GBNF (TypeScript)

A TypeScript port of `reference_implementation/` (the Python `gbnf` package): a library for
parsing `.gbnf` grammar files and walking the resulting grammar graph.

## Usage

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "foo" | "bar"');
state = state.add('b');
[...state]; // [{ type: 'char', value: [97] }]
```

`GBNF(grammar, initialString?)` returns a `ParseState`, which is iterable over the set of rules
that may come next. `state.add(text)` returns a new `ParseState` advanced by `text`, and throws an
`InputParseError` if the text cannot be parsed. An invalid grammar throws a `GrammarParseError`.

Exports: `GBNF` (default and named), `ParseState`, `Graph`, `RuleType`, `RuleChar`,
`RuleCharExclude`, `RuleEnd`, `RuleRef`, `GrammarParseError`, `InputParseError`.

## Layout

The module structure mirrors the Python package, with `snake_case` files renamed to `kebab-case`
and identifiers to `camelCase`:

| Python | TypeScript |
| --- | --- |
| `gbnf/GBNF.py` | `src/GBNF.ts` |
| `gbnf/rules_builder/` | `src/rules-builder/` |
| `gbnf/grammar_parser/` | `src/grammar-parser/` |
| `gbnf/grammar_graph/` | `src/grammar-graph/` |
| `gbnf/utils/` | `src/utils/` |

Python protocol methods map to their JS equivalents: `__iter__` → `[Symbol.iterator]`, `__len__` →
`size`, name-mangled `__attrs__` → `#privateFields`.

## Tests

```sh
npx vitest run --config vitest.config.unit.ts
```

## Deliberate differences from the reference

These are cases where the Python implementation raises an unintended error or relies on
unspecified ordering; the port implements the behaviour the reference code clearly intends.

- **Malformed grammars raise `GrammarParseError` instead of crashing.** Unterminated `"..."`,
  `[...]`, and `(...)` groups make Python raise `IndexError: string index out of range` from
  unchecked indexing. TypeScript indexing returns `undefined` instead, so the port reaches the
  reference's own error paths (`Unexpected end of grammar input, failed to complete parse`,
  `Expecting ')' at N`).
- **A grammar with no `root` symbol raises `GrammarParseError`.** Python does
  `if symbol_ids["root"] is None`, which raises `KeyError: 'root'` before the intended
  `Grammar does not contain a 'root' symbol` error can be reported.
- **`Graph.print()` works.** In Python it always raises `AttributeError: 'RuleEnd' object has no
  attribute 'type'`, since `type` only exists on the rules' `__dict__` property. Rules carry a real
  `type` field here, so printing renders `end` as intended.
- **Referenced-node ordering is deterministic.** `RuleRef.nodes` is a Python `set`, whose iteration
  order follows `id()`-based hashing and varies between runs; the port uses an insertion-ordered
  `Set`, so the rules yielded by a `ParseState` always follow grammar order.
