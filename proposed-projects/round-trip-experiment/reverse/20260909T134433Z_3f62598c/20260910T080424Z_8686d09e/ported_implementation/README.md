# GBNF (TypeScript port)

A TypeScript port of the Python [`gbnf`](../reference_implementation) library: a
parser for `.gbnf` grammar files that tells you, at any point in a string, which
characters may come next.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

const state = GBNF(`
root  ::= "yes" | "no"
`);
```

If the grammar is invalid, `GBNF` throws a `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which can be iterated over
(or iterated explicitly with `state.rules()`):

```ts
for (const rule of state) {
  console.log(rule);
  // { type: 'char', value: [ 121 ] }   // "y"
  // { type: 'char', value: [ 110 ] }   // "n"
}
```

`state` cannot be indexed directly, but spreads into an array with `[...state]`.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]);   // [{ type: 'char', value: [73] }]   // "I"
state = state.add('I li');
console.log([...state]);   // [{ type: 'char', value: [107] }]  // "k"
state = state.add('ke gree');
console.log([...state]);   // [{ type: 'char', value: [110] }]  // "n"
```

The rules returned are:

- `RuleChar` — `value` holds code points to match, or two element `[start, end]`
  arrays denoting an inclusive range within which a code point may appear.
- `RuleCharExclude` — the same, for code points that must _not_ match.
- `RuleEnd` — denotes a valid end of a string.

Each carries a `type` of `RuleType.CHAR`, `RuleType.CHAR_EXCLUDE` or
`RuleType.END`, whose values are the strings `"char"`, `"char_exclude"` and
`"end"` — the same values the Python library uses.

## API mapping

The module layout mirrors the reference tree, with names converted to
`camelCase`:

| Python                            | TypeScript                       |
| --------------------------------- | -------------------------------- |
| `GBNF(grammar, initial_string)`    | `GBNF(grammar, initialString)`   |
| `state.add(input)`                 | `state.add(input)`               |
| `state(input)`                     | `state.add(input)`               |
| `list(state)`                      | `[...state]`                     |
| `state.size` / `len(state)`        | `state.size`                     |
| `state.grammar`                    | `state.grammar`                  |
| `is_range(value)`                  | `isRange(value)`                 |
| `err.error_for_most_recent_input`  | `err.errorForMostRecentInput`    |
| `err.src`                          | `err.src`                        |

`GrammarParseError` and `InputParseError` extend `Error`; their rendered
messages (including the caret position block) match the reference byte for byte.

The Python state object is callable (`state(input)`); a class instance cannot be
called in JavaScript, so `state.add(input)` is the only spelling here.

Rules are plain objects rather than class instances, so they compare structurally
and serialize with `JSON.stringify` without ceremony. `RuleRef` — which is never
exposed to callers — remains a class, because the graph relies on its identity.

## Tests

The generated suite in `/workspace/tests/typescript` has been copied into
`tests/`, along with its config:

```sh
npx vitest run --config vitest.config.unit.ts
```

That covers all 773 cases of the generated suite.

> This image has no local `node_modules`; `vitest` is installed globally, so
> `node_modules/vitest` is a symlink into the global tree to let vite resolve it.
> A normal checkout would `npm install` instead.

### Differential testing

The port was additionally checked against the Python reference by running the
same grammars and inputs through both and comparing the traces — the rules
yielded on construction, after applying a whole input, and after applying that
input one character at a time, plus the exact text of any error thrown. Grammars
were randomly mutated to exercise the error paths, reusing the corpus builder in
`reference_implementation/tools/differential/run.py`.

Across roughly 2,600 grammars and 22,000 inputs, every trace matched except for
stack overflows on left-recursive grammars — see below.

## Deviations from the reference

Behaviour is otherwise identical, including error message text. These two cases
differ, both because the language differs rather than by choice:

1. **Stack overflow on a left-recursive grammar** surfaces as `RangeError:
   Maximum call stack size exceeded` rather than Python's `RecursionError`. V8
   also reaches its limit at a deeper nesting depth than CPython does.
2. **Characters outside the Basic Multilingual Plane.** Input is read as code
   points, as the reference does, so an emoji counts as one character. Error
   carets, however, are positioned with JavaScript's UTF-16 string lengths, so a
   caret that follows an astral character may sit one column further right than
   the reference puts it. Everything in the BMP — which includes every case in
   the test suites — behaves identically.

The reference's own three deviations from the _original_ JavaScript library
(the unreachable "Grammar does not contain a root symbol" branch, the
`Undefined rule identifier` error for a rule whose slot precedes a defined rule,
and raising on an escape with no hex digits instead of silently building a rule
that can never match) are all preserved here, since the Python implementation is
what this port follows.

## Type checking

`tsconfig.json` targets `NodeNext` with `strict` and `verbatimModuleSyntax`
enabled. No `typescript` package is available in this image and the registry is
unreachable, so `tsc` has not been run against it; the suite executes through
vitest's esbuild transform, which strips types without checking them.
