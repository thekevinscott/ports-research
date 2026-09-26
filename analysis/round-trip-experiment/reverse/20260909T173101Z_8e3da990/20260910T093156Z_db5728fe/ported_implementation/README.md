# GBNF (TypeScript port)

A TypeScript port of `reference_implementation/` (the Python `gbnf` package): a
library for parsing GBNF grammars.

## Usage

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "yes" | "no"');
for (const rule of state) {
  console.log(rule);
  // { type: 'char', value: [121] }
  // { type: 'char', value: [110] }
}
```

States are immutable; `add` returns the next state:

```ts
let state = GBNF('root ::= "I like green eggs and ham"');
state = state.add('I li');
[...state].map(rule => rule.value);   // [[107]]  -> "k"
state = state.add('ke gree');
[...state].map(rule => rule.value);   // [[110]]  -> "n"
```

The rules returned are `RuleChar`, `RuleCharExclude` and `RuleEnd`. Each has a
`type` and (except for `RuleEnd`) a `value` of code points and inclusive
`[start, end]` ranges.

Invalid grammars throw `GrammarParseError`; input that the grammar cannot match
throws `InputParseError`.

## Layout

The module layout mirrors the reference, with snake_case file names converted
back to kebab-case:

| reference | port |
| --- | --- |
| `__init__.py` | `src/index.ts` |
| `gbnf.py` | `src/gbnf.ts` |
| `rules_builder/` | `src/rules-builder/` |
| `grammar_parser/` | `src/grammar-parser/` |
| `grammar_graph/` | `src/grammar-graph/` |
| `utils/` | `src/utils/` |

Functions and methods are camelCase; the reference's snake_case names and its
`utils/strings.py` (which emulated JS string indexing) are gone, since `src[pos]`
is native here.

## Tests

```sh
cp -r /workspace/tests/typescript tests
cp tests/vitest.config.unit.ts .
npx vitest run --config vitest.config.unit.ts
```

Behaviour was also checked directly against the reference implementation across
~1,500 grammar/input cases — rules, state sizes, error messages and the graph's
debug `print()` output all match.

## Deviations from the reference

1. **Error classes follow JS.** The messages are identical, but a grammar that
   can recurse without consuming input (`("a"*)+`, `("a"?)*`) throws a
   `RangeError` rather than a `RecursionError`, and a grammar with no `root`
   symbol throws an `Error` rather than a `KeyError`.

2. **Positions within the grammar are UTF-16 offsets**, since that is what
   indexing a JS string yields; the reference counts code points. This only
   shows up in the caret position of an error message for a grammar containing
   characters outside the Basic Multilingual Plane. Rules and input are still
   whole code points on both sides, so such a character is one rule and one
   input step, and `\U0001F600`-style escapes match the input they describe.

3. **Python-only affordances are gone.** Rules are plain objects rather than
   class instances (so they compare structurally without help), states are
   iterated with `for...of` rather than called, and there are no name aliases.

Graph traversal is iterative here as it is in the reference, so deeply nested
input does not depend on the JS engine's stack.
