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
import GBNF from 'gbnf';

const state = GBNF(`
root  ::= "yes" | "no"
`);
for (const rule of state) {
  console.log(rule);
  // { type: 'char', value: [121] }
  // { type: 'char', value: [110] }
}
```

`state` is iterable. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but can easily be spread into an
array with `[...state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
import GBNF from 'gbnf';

let state = GBNF('root  ::= "I like green eggs and ham"');
console.log([...state]); // [{ type: 'char', value: [73] }]
state = state.add('I li');
console.log([...state]); // [{ type: 'char', value: [107] }]
state = state.add('ke gree');
console.log([...state]); // [{ type: 'char', value: [110] }]
```

If the input cannot be parsed, an `InputParseError` is thrown.

The possible rules returned include:

- `RuleChar` - contains a list of either numbers representing code points to match, _or_ a
  two element array denoting a range within which a code point may appear.
- `RuleCharExclude` - contains a list of numbers representing code points _not_ to match,
  _or_ a two element array denoting a range within which a code point may _not_ appear.
- `RuleEnd` - denotes a valid end of a string.

## Differences from the Python implementation

- Names are camelCase (`errorForMostRecentInput`, `isRange`, `buildRuleStack`), except for
  the `GBNF` entry point and the class names, which are kept as-is.
- Rules are plain objects rather than classes, and so compare structurally without any
  help: `expect({ type: 'char', value: [102] }).toEqual(rule)`.
- The errors are plain `Error` subclasses and so compare by identity; two equivalent
  errors are distinct objects with equal `message`s.
- `ParseState` exposes `add`, `rules`, `size` and `grammar`; the Python `__call__` /
  `__add__` / `__len__` sugar has no TypeScript equivalent.

## Tests

The generated suite lives in `../tests/typescript`; the copy in `tests/` is what runs.

```sh
cd ported_implementation
cp -r ../tests/typescript tests
cp tests/vitest.config.unit.ts .
npx vitest run --config vitest.config.unit.ts
```

`vitest` is only available as a global install in this environment, so `node_modules`
holds a symlink to it rather than a real dependency tree.
