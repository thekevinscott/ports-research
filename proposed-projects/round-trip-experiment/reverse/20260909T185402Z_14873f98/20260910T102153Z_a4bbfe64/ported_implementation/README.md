# GBNF

A library for parsing `.gbnf` grammar files in TypeScript. This is a port of the Python
implementation in `reference_implementation/`.

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
  // RuleChar { type: 'char', value: [121] }  -> 'y'.charCodeAt(0)
  // RuleChar { type: 'char', value: [110] }  -> 'n'.charCodeAt(0)
}
```

`state` is iterable. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but can easily be spread into an
array with `[...state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]); // [RuleChar { value: [73] }]  -> 'I'
state = state.add('I li');
console.log([...state]); // [RuleChar { value: [107] }] -> 'k'
state = state.add('ke gree');
console.log([...state]); // [RuleChar { value: [110] }] -> 'n'
```

If the input does not match the grammar, `add` throws an `InputParseError`.

The possible rules returned include:

- `RuleChar` — `value` is an array of either code points to match, _or_ two-element
  arrays denoting an inclusive range within which a code point may appear.
- `RuleCharExclude` — `value` is an array of code points _not_ to match, _or_
  two-element arrays denoting a range within which a code point may _not_ appear.
- `RuleEnd` — denotes a valid end of a string.

## Differences from the Python implementation

- Methods and functions use `camelCase`; classes keep their original names.
- `ParseState` is advanced with `state.add(input)`; the Python conveniences
  `state + input` and `state(input)` have no TypeScript equivalent.
- `error_for_most_recent_input` is `errorForMostRecentInput`, and the other error
  properties are likewise camelCased.
- Grammar text is indexed as UTF-16 code units (JavaScript's native string indexing),
  while input strings are converted to code points, matching the Python `ord()`
  behaviour.

## Tests

```sh
cp -r ../tests/typescript tests
cp tests/vitest.config.unit.ts .
npx vitest run --config vitest.config.unit.ts
```
