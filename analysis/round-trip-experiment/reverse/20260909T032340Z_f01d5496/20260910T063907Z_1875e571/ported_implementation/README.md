# GBNF

A library for parsing `.gbnf` grammar files in TypeScript. A port of the Python
implementation in `../reference_implementation`.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

const state = GBNF(`
root  ::= "yes" | "no"
`);
```

If the grammar is invalid, `GBNF` throws a `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```ts
for (const rule of state) {
  console.log(rule);
  // RuleChar { value: [121] }  // "y"
  // RuleChar { value: [110] }  // "n"
}
```

`state` is iterable. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but can easily be spread into an
array with `[...state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]); // [RuleChar { value: [73] }]   // "I"
state = state.add('I li');
console.log([...state]); // [RuleChar { value: [107] }]  // "k"
state = state.add('ke gree');
console.log([...state]); // [RuleChar { value: [110] }]  // "n"
```

The possible rules returned include:

- `RuleChar` - contains a list of either numbers representing code points to match, _or_
  a two element array denoting a range within which a code point may appear.
- `RuleCharExclude` - contains a list of numbers representing code points _not_ to
  match, _or_ a two element array denoting a range within which a code point may _not_
  appear.
- `RuleEnd` - denotes a valid end of a string.

If the input does not match the grammar, `add` throws an `InputParseError`.

## Layout

The module tree mirrors the reference implementation:

| TypeScript                          | Python                              |
| ----------------------------------- | ----------------------------------- |
| `src/gbnf.ts`                       | `gbnf/gbnf.py`                      |
| `src/grammar-graph/`                | `gbnf/grammar_graph/`               |
| `src/grammar-parser/`               | `gbnf/grammar_parser/`              |
| `src/rules-builder/`                | `gbnf/rules_builder/`               |
| `src/utils/`                        | `gbnf/utils/`                       |

## Tests

```sh
npx vitest run --config vitest.config.unit.ts
```
