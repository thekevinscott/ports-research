# GBNF (TypeScript port)

A TypeScript port of the Python `gbnf` package in `reference_implementation/` — a
library for parsing `.gbnf` grammar files.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

const state = GBNF('root ::= "yes" | "no"');
```

If the grammar is invalid, `GBNF` throws a `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```ts
for (const rule of state) {
  console.log(rule);
  // RuleChar { type: 'char', value: [121] }   // 'y'
  // RuleChar { type: 'char', value: [110] }   // 'n'
}
```

`state` is iterable. It cannot be indexed directly, but spreads into an array with
`[...state]`. `state.size` gives the number of distinct rules.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]);  // [{ type: 'char', value: [73] }]   // 'I'
state = state.add('I li');
console.log([...state]);  // [{ type: 'char', value: [107] }]  // 'k'
state = state.add('ke gree');
console.log([...state]);  // [{ type: 'char', value: [110] }]  // 'n'
```

Input may be a `string`, a single code point (`number`), or an array of code
points. Input the grammar cannot accept throws an `InputParseError`.

The possible rules returned include:

- `RuleChar` (`RuleType.CHAR`, `'char'`) — `value` holds code points to match, where
  an entry may itself be a two-element `[start, end]` range.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`, `'char_exclude'`) — as above, but code
  points that must _not_ match.
- `RuleEnd` (`RuleType.END`, `'end'`) — denotes a valid end of a string.

Rules are plain data objects, so they are straightforward to assert against:

```ts
expect([...GBNF('root ::= [a-z]')]).toEqual([{ type: 'char', value: [[97, 122]] }]);
```

## Layout

The module tree mirrors the reference implementation one-for-one (snake_case file
names become kebab-case):

| reference | port |
| --- | --- |
| `gbnf.py` | `src/gbnf.ts` |
| `grammar_graph/*` | `src/grammar-graph/*` |
| `grammar_parser/build_rule_stack.py` | `src/grammar-parser/build-rule-stack.ts` |
| `rules_builder/*` | `src/rules-builder/*` |
| `utils/**` | `src/utils/**` |

Functions are exposed under camelCase names. The reference's `utils/js_compat.py`
has no counterpart here: it exists only to reproduce JavaScript's `String` indexing,
`JSON.stringify` and `parseInt` semantics in Python, which are native here.

## Tests

```bash
vitest run --config vitest.config.unit.ts
```

## Intentional divergences from the reference

1. **Unicode beyond the BMP.** The reference walks Python strings as code points; the
   port walks JavaScript strings as UTF-16 code units. Results are identical for BMP
   text. For astral characters the port builds a rule for the full code point (e.g.
   `root ::= "\U0001F600"`) but then feeds it lone surrogates, so the match fails —
   where the reference matches `"😀"`.

2. **Error types.** Python's `Exception` becomes `Error`, and `SymbolIds` lookups
   raise a plain `Error` whose message matches the reference's `SymbolIdsKeyError`.
   Blowing the stack on a left-recursive grammar raises `RangeError` rather than
   `RecursionError`.

3. **Naming-only surface.** The reference exposes both snake_case and camelCase
   aliases (`is_range`/`isRange`, `parse_char`/`parseChar`, …) for parity with *its*
   reference. The port exposes only the camelCase names.
