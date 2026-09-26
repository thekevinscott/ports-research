# GBNF

A library for parsing `.gbnf` grammar files in TypeScript. This is a port of the Python
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
  // RuleChar([102])
  // RuleChar([110])
}
```

`state` is iterable. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but is easily spread into an array
with `[...state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
import GBNF from 'gbnf';

let state = GBNF(`
root  ::= "I like green eggs and ham"
`);
console.log([...state]);   // [RuleChar([73])]
state = state.add('I li');
console.log([...state]);   // [RuleChar([107])]
state = state.add('ke gree');
console.log([...state]);   // [RuleChar([110])]
```

If the input does not match the grammar, `add` throws an `InputParseError`.

The possible rules returned include:

- `RuleChar` — holds a list of either numbers representing code points to match, _or_ a
  two-number list denoting a range within which a code point may appear.
- `RuleCharExclude` — holds a list of numbers representing code points _not_ to match,
  _or_ a two-number list denoting a range within which a code point may _not_ appear.
- `RuleEnd` — denotes a valid end of a string.

## Tests

```sh
cd /workspace/ported_implementation
npx vitest run --config vitest.config.unit.ts
```
