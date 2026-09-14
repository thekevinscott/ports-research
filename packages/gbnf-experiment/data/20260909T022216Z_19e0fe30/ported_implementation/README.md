# GBNF (TypeScript)

A TypeScript port of `reference_implementation/` — a library for parsing `.gbnf`
grammar files and walking the resulting grammar graph one character at a time.

## Usage

```ts
import { GBNF } from './src/index.js';

const state = GBNF('root ::= "foo"');
[...state]; // [ RuleChar { value: [102] } ]  -- the parser will accept "f" next

const next = state.add('f');
[...next]; // [ RuleChar { value: [111] } ]   -- now it will accept "o"

next.add('z'); // throws InputParseError
```

`GBNF(grammar, initialString?)` returns a `ParseState`. A `ParseState` is
iterable, yielding the deduplicated set of `RuleChar` / `RuleCharExclude` /
`RuleEnd` rules that may come next. `state.add(text)` returns a *new*
`ParseState`; it throws `InputParseError` if the text is not accepted, and
`GBNF` throws `GrammarParseError` for an invalid grammar.

## Layout

The module structure mirrors the reference package one-to-one:

| reference (python)                    | port (typescript)                     |
| ------------------------------------- | ------------------------------------- |
| `gbnf/GBNF.py`                        | `src/GBNF.ts`                         |
| `gbnf/grammar_graph/*.py`             | `src/grammar-graph/*.ts`              |
| `gbnf/grammar_parser/*.py`            | `src/grammar-parser/*.ts`             |
| `gbnf/rules_builder/*.py`             | `src/rules-builder/*.ts`              |
| `gbnf/utils/**.py`                    | `src/utils/**.ts`                     |

## Tests

```sh
cd /workspace/ported_implementation
npm test          # or: vitest run
```

`tests/` is a translation of the python suite in `/workspace/tests/python`,
which imports `gbnf` as a python package and so cannot run against this port
directly. Every case was extracted mechanically from the python
`@pytest.mark.parametrize` data into `tests/fixtures/*.json`, so the two suites
exercise the same 773 cases:

| suite                                        | cases |
| -------------------------------------------- | ----- |
| `tests/validation/validate-grammar.test.ts`   | 26    |
| `tests/validation/validate-input.test.ts`     | 68    |
| `tests/iteration/iteration.test.ts`           | 21    |
| `tests/iteration/iteration-with-an-initial-string.test.ts` | 92 |
| `tests/iteration/iteration-with-additional-strings.test.ts` | 113 |
| `tests/iteration/grammars.test.ts`            | 453   |

Three more suites (87 cases) check the port against the reference directly,
covering ground the translated suite does not:

- `tests/differential.test.ts` (8) replays every grammar test case character by
  character and compares the accepted rule set after *each* character against a
  trace recorded from the reference — 23,876 parse-state snapshots, where
  `grammars.test.ts` only asserts that parsing does not throw.
- `tests/error-messages.test.ts` (76) compares rendered error text against
  strings recorded from the reference. The translated tests build their
  expectation with this package's own error classes, so they would not notice
  the message format drifting.
- `tests/graph-print.test.ts` (3) pins down `Graph.print`, which has no coverage
  in the python suite (see below).

Regenerate the recorded fixtures with:

```sh
python3 tools/record-reference-trace.py tests/fixtures/reference-trace.json
python3 tools/record-reference-errors.py tests/fixtures/reference-errors.json
```

### Type checking

`tsconfig.json` is set up for `tsc --noEmit`, but this environment has no
network access and no `typescript` package in any cache, so the types have not
been machine-checked. Vitest transpiles the TypeScript with esbuild, which
strips types without checking them — run `npx tsc --noEmit` once a registry is
reachable.

## Notable behaviour notes

- **Rule ordering is not part of the contract.** The reference yields rules in
  an order derived from python `set` iteration over graph nodes, which is keyed
  on object identity and therefore differs between runs of the same input. This
  port uses insertion-ordered `Set`/`Map`, so its ordering is deterministic. The
  differential test compares sorted rule sets for that reason.
- **Errors.** `GrammarParseError` and `InputParseError` extend `Error` and
  produce byte-identical messages to the reference. The reference compares
  errors with `__eq__` on the rendered message; the port exposes `.equals()`
  for the same purpose.
- **Code points.** String input is iterated by code point (`[...src]`), matching
  python's `for c in s`, rather than by UTF-16 code unit.
- **`Graph.print` works here.** The reference prints a non-char, non-ref rule as
  `rule.type`, an attribute its `Rule` classes never define, so printing any
  graph containing a `RuleEnd` node — every graph — raises `AttributeError`.
  Rules carry a `type` in this port, so `print()` returns the intended rendering.
- **Missing `root` symbol.** The reference reads `symbol_ids["root"]` and
  compares it to `None`, which raises `KeyError` before it can report the
  intended error. The port checks for the missing key and raises the intended
  `GrammarParseError("Grammar does not contain a 'root' symbol")`. No test
  covers this path.
- A malformed hex escape (`\xZZ`) raises a plain `Error` here, matching the
  reference's `ValueError` from `int(..., 16)` rather than a `GrammarParseError`.
