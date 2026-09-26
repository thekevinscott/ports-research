# GBNF (TypeScript)

A TypeScript port of the Python `gbnf` library in `../reference_implementation`. It
parses `.gbnf` grammar files and incrementally validates input against them.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "yes" | "no"');
```

If the grammar is invalid, `GBNF` throws a `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which can be iterated over to see
which rules could come next (`state.rules()` returns the same iterator):

```ts
for (const rule of state) {
  console.log(rule);
  // RuleChar { type: 'char', value: [121] }  -> "y"
  // RuleChar { type: 'char', value: [110] }  -> "n"
}
```

States are *immutable*. To parse more input, call `state.add()`:

```ts
state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]); // [RuleChar { value: [73] }]
state = state.add('I li');
console.log([...state]); // [RuleChar { value: [107] }]
state = state.add('ke gree');
console.log([...state]); // [RuleChar { value: [110] }]
```

Input that the grammar does not allow throws an `InputParseError`. An initial string can
be passed straight to `GBNF`: `GBNF(grammar, 'I li')`.

Rules are one of `RuleChar`, `RuleCharExclude` (each with a `value` array of code points
and inclusive `[start, end]` ranges) or `RuleEnd` (the input may stop here).

## Layout

The module layout mirrors the reference implementation, with names converted back to
`kebab-case` files and `camelCase` bindings:

| Python                             | TypeScript                       |
| ---------------------------------- | -------------------------------- |
| `gbnf/gbnf.py`                     | `src/gbnf.ts`                    |
| `gbnf/rules_builder/`              | `src/rules-builder/`             |
| `gbnf/grammar_parser/`             | `src/grammar-parser/`            |
| `gbnf/grammar_graph/`              | `src/grammar-graph/`             |
| `gbnf/utils/`                      | `src/utils/`                     |

Two things the reference spells out explicitly, because Python and JavaScript disagree,
collapse back into plain JavaScript here: `charAt` (`src/rules-builder/char-at.ts`) still
returns `''` past the end of a string, and a rule id that is never defined is a genuine
sparse-array hole in `RulesBuilder.rules` rather than an explicit `None`. `src/gbnf.ts`
walks that array by index rather than with `map`, so the holes are still visited.

## Deviations from the reference implementation

The port is behaviour-for-behaviour identical to the reference. A differential harness
walked both implementations character by character over the bundled grammars, hand-written
edge cases and several hundred fuzzed grammar mutations, comparing the rule set at every
step as well as every error message; the only difference is:

1. Internal invariant violations (`Encountered alt without anything before it` and
   friends) throw a plain `Error`, where the reference raises Python's `ValueError`. The
   messages are unchanged.

The reference's documented deviations from *its* reference — raising a `GrammarParseError`
for a missing `root` symbol, for an undefined rule identifier reached through a generated
sub-rule, and for a malformed hex escape — are all preserved here.

## Tests

The TypeScript test suite lives in `tests/` (copied from `../tests/typescript`):

```sh
npx vitest run --config vitest.config.unit.ts
```

`vitest.config.unit.ts` aliases `gbnf` to `src/index.ts`.

## Consuming the source

The package has no build step; `main` points straight at `src/index.ts`, and relative
imports use explicit `.ts` extensions so that bundlers, `vitest`, and Node's own TypeScript
support (`node --experimental-transform-types`) can all resolve them.
