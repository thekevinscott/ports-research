# GBNF (TypeScript)

A TypeScript port of the Python GBNF grammar parser in
[`../reference_implementation`](../reference_implementation). A library for
parsing `.gbnf` grammar files.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

const state = GBNF(`
root  ::= "yes" | "no"
`);
```

If the grammar is invalid, `GBNF` throws `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which can be iterated
over (`state.rules()` yields the same rules):

```ts
import GBNF from 'gbnf';

const state = GBNF('root ::= "yes" | "no"');
for (const rule of state) {
  console.log(rule);
  // { type: 'char', value: [121] }
  // { type: 'char', value: [110] }
}
```

States are _immutable_. To parse a new token, call `state.add()`:

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]); // [{ type: 'char', value: [73] }]
state = state.add('I li');
console.log([...state]); // [{ type: 'char', value: [107] }]
state = state.add('ke gree');
console.log([...state]); // [{ type: 'char', value: [110] }]
```

Input that the grammar cannot accept throws `InputParseError`.

The possible rules returned include:

- `RuleChar` (`RuleType.CHAR`) — `value` holds either code points to match, or
  a `[start, end]` pair denoting a range within which a code point may appear.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`) — the same, for code points _not_
  to match.
- `RuleEnd` (`RuleType.END`) — denotes a valid end of a string.

`ruleToDict(rule)` renders any rule as plain data
(`{ type: 'char', value: [102] }`), which is handy for comparisons and
serialization.

## Layout

The package mirrors the reference implementation module for module:

| Reference (Python)          | Port (TypeScript)           |
| --------------------------- | --------------------------- |
| `gbnf/gbnf.py`              | `src/gbnf.ts`               |
| `gbnf/rules_builder/`       | `src/rules-builder/`        |
| `gbnf/grammar_parser/`      | `src/grammar-parser/`       |
| `gbnf/grammar_graph/`       | `src/grammar-graph/`        |
| `gbnf/utils/`               | `src/utils/`                |

`src/index.ts` is the entry point the test suite imports.

## Tests

The generated suite in `/workspace/tests/typescript` is copied to `tests/`, and
covers 773 cases:

```sh
vitest run --config vitest.config.unit.ts
```

The config aliases `gbnf` to `src/index.ts`.

## Notes on the port

- **Code points, not UTF-16 code units.** The reference indexes strings by code
  point, so `src/utils/js.ts` splits a source into code points (memoising the
  most recent split) and the parser indexes that array. `"😀"` is therefore one
  rule matching one character, exactly as in the reference, rather than the
  surrogate pair a raw JS string index would yield.
- **`json.dumps` spacing.** Two error messages embed serialized values, and
  Python's `json.dumps` separates items with `", "` where `JSON.stringify`
  packs them tightly. `src/utils/json.ts` reproduces Python's spacing so the
  messages match.
- **Calling a state.** The reference's `ParseState` is callable
  (`state('...')`, equivalent to `state.add('...')`). A JS class instance
  cannot be called, so only `add` is provided.
- **Dunder methods.** `__iter__` becomes `[Symbol.iterator]`, `__len__` becomes
  the `size` getter, and `__repr__` becomes `toString`. `__bool__` needs no
  equivalent: a state object is always truthy.
