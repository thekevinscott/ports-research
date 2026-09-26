# GBNF (TypeScript)

A TypeScript port of `reference_implementation/` — a library for parsing `.gbnf` grammar
files and incrementally validating input against them.

## Usage

```ts
import { GBNF } from 'gbnf';

let state = GBNF('root ::= "foo"');
state = state.add('f');

for (const rule of state) {
  // RuleChar / RuleCharExclude / RuleEnd describing what may come next
}
```

`GBNF(grammar, initialString?)` returns a `ParseState`. A `ParseState` is iterable (it
yields the rules that could match next), exposes `size` and `grammar`, and `add(text)`
returns a new `ParseState`. Invalid grammars throw `GrammarParseError`; invalid input
throws `InputParseError`.

## Layout

The module layout mirrors the Python reference one-to-one, with `snake_case` filenames
renamed to `camelCase`:

| reference (Python)              | port (TypeScript)             |
| ------------------------------- | ----------------------------- |
| `gbnf/GBNF.py`                  | `src/GBNF.ts`                 |
| `gbnf/rules_builder/`           | `src/rulesBuilder/`           |
| `gbnf/grammar_parser/`          | `src/grammarParser/`          |
| `gbnf/grammar_graph/`           | `src/grammarGraph/`           |
| `gbnf/utils/`                   | `src/utils/`                  |

## Tests

```sh
cd /workspace/ported_implementation
vitest run
```

`tests/` is a translation of `/workspace/tests/python`. The parametrized case data was
extracted from the Python decorators programmatically rather than retyped, so the suites
run the same 773 cases; the grammar fixtures under `tests/iteration/grammars/` are copied
verbatim.

## Known divergences from the reference

Everything below was found by a differential harness that ran both implementations over
2,853 (grammar, prefix, next-character) combinations drawn from the test grammars and
every grammar in the test suite. Outside of these two classes, the two implementations
produced byte-identical results.

1. **Rule ordering is deterministic here, arbitrary in the reference.**
   `GraphPointer.resolve` iterates a `set` of graph nodes. Python sets of
   identity-hashed objects have no defined order — re-running the reference over the same
   corpus changes the order of the emitted rules in ~11% of cases. The port uses an
   insertion-ordered `Set`, so rules come back in grammar order, deterministically. The
   ordered assertions in `iteration.test.ts` hold either way.

2. **`build_error_position` no longer crashes past the last line.**
   When an error position falls beyond the final line of a multi-line input, the
   reference indexes `lines[line_idx]` out of bounds and raises `IndexError` instead of
   the intended `InputParseError` (193 of the 2,853 combinations). The port ends the
   scan at the last line and reports the `InputParseError`.

Two smaller, related fixes:

- `Graph.print()` prints a rule's class name via `rule.type`, which the reference's `Rule`
  never defines — printing any graph containing a `RuleEnd` raises `AttributeError` there.
  The rules in this port expose `type`, so `print()` works.
- Malformed hex escapes (`\xZZ`) raise a `GrammarParseError` rather than silently parsing
  as `0`, matching the reference's `int(..., 16)` raising on bad input.

## Notes on the translation

- Python strings index by code point, JavaScript strings by UTF-16 code unit. Input
  handling and error positions are code-point based (see `src/utils/codePointLength.ts`)
  to match the reference; the grammar scanner indexes by code unit, which is equivalent
  for every character in the Basic Multilingual Plane, and `parseChar` reads whole code
  points so astral characters in a grammar still parse correctly.
- Python's `OrderedDict` insertion semantics map directly onto `Map`, so `Pointers` and
  the graph's root/rule bookkeeping preserve the reference's ordering.
- `src/utils/validateNonEmpty.ts` is carried over from the reference, where it is
  referenced only as unused dataclass field metadata.

There is no `typescript` package available in this offline environment, so the sources are
published (and consumed by `vitest`) as `.ts` directly; `tsconfig.json` is set up for a
`tsc` build once dependencies can be installed.
