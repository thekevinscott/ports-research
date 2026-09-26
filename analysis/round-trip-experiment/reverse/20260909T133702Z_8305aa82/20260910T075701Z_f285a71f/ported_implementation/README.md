# GBNF

A library for parsing `.gbnf` grammar files in TypeScript. This is a port of the
Python reference implementation in `../reference_implementation`.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

const state = GBNF(`
root  ::= "yes" | "no"
`);
```

If the grammar is invalid, `GBNF` throws `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```ts
import GBNF from 'gbnf';

const state = GBNF(`
root  ::= "yes" | "no"
`);
for (const rule of state) {
  console.log(rule);
  // RuleChar { type: 'char', value: [121] }   // 'y'.charCodeAt(0)
  // RuleChar { type: 'char', value: [110] }   // 'n'.charCodeAt(0)
}
```

`state` is iterable. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but can easily be spread
into an array with `[...state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
import GBNF from 'gbnf';

let state = GBNF('root  ::= "I like green eggs and ham"');
console.log([...state]); // [RuleChar { type: 'char', value: [73] }]   // 'I'
state = state.add('I li');
console.log([...state]); // [RuleChar { type: 'char', value: [107] }]  // 'k'
state = state.add('ke gree');
console.log([...state]); // [RuleChar { type: 'char', value: [110] }]  // 'n'
```

The possible rules returned include:

- `RuleChar` - contains a list of either numbers representing code points to
  match, _or_ a two-element tuple denoting a range within which a code point may
  appear.
- `RuleCharExclude` - contains a list of numbers representing code points _not_
  to match, _or_ a two-element tuple denoting a range within which a code point
  may _not_ appear.
- `RuleEnd` - denotes a valid end of a string.

Invalid input throws `InputParseError`.

## Layout

The module layout mirrors the reference implementation:

| Reference (Python)          | Port (TypeScript)           |
| --------------------------- | --------------------------- |
| `gbnf/gbnf.py`              | `src/gbnf.ts`               |
| `gbnf/grammar_graph/`       | `src/grammar-graph/`        |
| `gbnf/grammar_parser/`      | `src/grammar-parser/`       |
| `gbnf/rules_builder/`       | `src/rules-builder/`        |
| `gbnf/utils/`               | `src/utils/`                |

## Tests

The generated suite from `/workspace/tests/typescript` is copied into `tests/`,
with its config at `vitest.config.unit.ts` (aliasing `gbnf` to `src/index.ts`).

```sh
cd /workspace/ported_implementation
npx vitest run --config vitest.config.unit.ts
```
