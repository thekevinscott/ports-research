# gbnf (TypeScript)

A TypeScript port of the [`gbnf`](../reference_implementation) Python library: a parser for
GBNF grammar files.

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
  // { type: 'char', value: [ 121 ] }   // "y"
  // { type: 'char', value: [ 110 ] }   // "n"
}
```

`state` is iterable (you can also call `state.rules()` for the iterator directly). It
cannot be indexed, but spreads into an array with `[...state]`.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]);      // [ { type: 'char', value: [ 73 ] } ]
state = state.add('I li');
console.log([...state]);      // [ { type: 'char', value: [ 107 ] } ]
state = state.add('ke gree');
console.log([...state]);      // [ { type: 'char', value: [ 110 ] } ]
```

The possible rules returned include:

- `RuleChar` (`RuleType.CHAR`) — `value` holds either code points to match, _or_ a
  two-element array denoting a range within which a code point may appear.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`) — `value` holds code points _not_ to match,
  _or_ a two-element array denoting a range within which a code point may _not_ appear.
- `RuleEnd` (`RuleType.END`) — denotes a valid end of a string.

Use `isRange` to tell the two forms of `value` apart:

```ts
import GBNF, { isRange } from 'gbnf';

const [rule] = [...GBNF('root ::= [a-z]')];
isRange(rule.value[0]); // true
```

Input may be a string, a single code point, or an array of code points. An input that the
grammar cannot match throws an `InputParseError`.

## Layout

The module layout mirrors the reference implementation:

| TypeScript                | Python                     |
| ------------------------- | -------------------------- |
| `src/gbnf.ts`             | `gbnf/gbnf.py`             |
| `src/rules-builder/`      | `gbnf/rules_builder/`      |
| `src/grammar-parser/`     | `gbnf/grammar_parser/`     |
| `src/grammar-graph/`      | `gbnf/grammar_graph/`      |
| `src/utils/`              | `gbnf/utils/`              |

`gbnf/utils/js.py` has no counterpart here: it exists in the reference only to reproduce
JavaScript string and `parseInt` semantics (UTF-16 code units, out-of-range indexing
yielding `undefined`, `parseInt` parsing the longest valid prefix), which TypeScript has
natively. Its call sites use the native equivalents:

| `js.py`                          | TypeScript                       |
| -------------------------------- | -------------------------------- |
| `to_utf16`                       | (no-op — strings are UTF-16)     |
| `to_code_units`                  | `charCodeAt` over the string     |
| `char_at`, `char_code_at`        | `src[pos]`, `src.charCodeAt(pos)`|
| `code_point_at`                  | `src.codePointAt(pos)`           |
| `from_char_code`, `from_code_point` | `String.fromCharCode`, `String.fromCodePoint` |
| `parse_int`                      | `parseInt`                       |
| `join`                           | `Array.prototype.join`           |

Likewise, the reference's `Rule` / `InternalRuleDef` class hierarchies and their
`to_json`/`__eq__` helpers exist to give Python objects JavaScript object-literal
semantics; here they are plain object types compared and serialized with
`JSON.stringify`.

## Tests

```sh
vitest run --config vitest.config.unit.ts
```

`tests/` is a copy of `/workspace/tests/typescript`, per that suite's README. All 773
tests pass.

## Fidelity notes

Behaviour was checked against the reference implementation case by case (rule streams,
graph renderings, and error class names plus messages, for both valid and invalid
grammars and inputs); the two agree exactly, including these inherited quirks:

- A grammar with no `root` symbol throws `GBNFError: SymbolIds does not contain key: root`
  from `SymbolIds.get`, before `gbnf.ts`'s "Grammar does not contain a root symbol" check
  can fire. That branch is kept, unreachable, as in the reference.
- While parsing, rules live in a sparse array; a rule identifier that is referenced but
  never defined leaves a hole in it. Validation skips holes and reports
  `GrammarParseError: Undefined rule identifier "..."`, as the reference does. (The
  reference's own upstream — the original JavaScript library — instead threw
  `TypeError: rule is not iterable` when the hole sat before the rule containing the bad
  reference. This only affects grammars that are rejected either way.)

One message differs by necessity: the unreachable "Grammar does not contain a root symbol.
Available symbols are: ..." interpolates the symbol list JavaScript-style (`a,b`) rather
than as a Python list repr (`['a', 'b']`).
