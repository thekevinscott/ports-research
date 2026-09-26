# gbnf (TypeScript)

A TypeScript port of the Python `gbnf` package in `../reference_implementation`: a
library for parsing [GBNF](https://github.com/ggerganov/llama.cpp/blob/master/grammars/README.md)
grammars and walking the resulting graph one code point at a time.

## Usage

```ts
import GBNF, { InputParseError } from 'gbnf';

let state = GBNF('root ::= "foo" | "bar"');
[...state].map(rule => rule.toJSON());
// [{ type: 'char', value: [102] }, { type: 'char', value: [98] }]

state = state.add('f');
[...state].map(rule => rule.toJSON());
// [{ type: 'char', value: [111] }]

[...state.add('oo')].map(rule => rule.toJSON());
// [{ type: 'end' }]

state.add('x'); // throws InputParseError
```

`GBNF(grammar, initialString = '')` returns a `ParseState`. Iterating a `ParseState`
yields the rules that may come next (`RuleChar`, `RuleCharExclude`, `RuleEnd`);
`add()` consumes more input and returns the next state, throwing `InputParseError`
when the input can no longer satisfy the grammar. An unparseable grammar throws
`GrammarParseError`.

## Layout

The module tree mirrors the reference implementation one-for-one, with names
converted back to `kebab-case` files and `camelCase` identifiers:

| Python                                 | TypeScript                            |
| -------------------------------------- | ------------------------------------- |
| `gbnf/__init__.py`                     | `src/index.ts`                        |
| `gbnf/gbnf.py`                         | `src/gbnf.ts`                         |
| `gbnf/rules_builder/*`                 | `src/rules-builder/*`                 |
| `gbnf/grammar_parser/build_rule_stack` | `src/grammar-parser/build-rule-stack` |
| `gbnf/grammar_graph/*`                 | `src/grammar-graph/*`                 |
| `gbnf/utils/*`                         | `src/utils/*`                         |

`gbnf/utils/js.py` has no counterpart: it exists to give the Python the JavaScript
string semantics the parsers rely on (`src[pos]` past the end of a string yields
`undefined` rather than throwing), which are native here. Its one piece with
behaviour of its own, `parse_int_hex`, survives as `src/utils/parse-hex.ts` —
it is deliberately stricter than `parseInt(src, 16)`, which would also accept a
leading sign or whitespace (`"\u+0042"`).

Where the reference relies on insertion-ordered `dict`s standing in for JavaScript
`Map`/`Set`, this port uses `Map`/`Set` directly (iteration order is load-bearing —
it determines the order in which rules come out of a `ParseState`). Rules are
compared by reference, as they are in the reference implementation.

### API differences

- `ParseState` is iterated with `for...of` / spread rather than Python's `__iter__`,
  and `state.add(input)` replaces the reference's callable-instance shorthand
  `state(input)`.
- `rule.toJSON()` replaces `rule.to_dict()`; `JSON.stringify(rule)` and
  `rule.serialize()` produce the same string the reference does.
- Internal invariant violations that the reference raises as `ValueError` are
  thrown as `Error` here, with the same message.

## Tests

```sh
cd /workspace/ported_implementation
npx vitest run --config vitest.config.unit.ts   # 773 tests
```

`tests/` is the generated suite from `/workspace/tests/typescript`, unmodified;
`vitest.config.unit.ts` aliases `gbnf` to `src/index.ts`.

The port was additionally differentially tested against the reference
implementation: 31 grammars × 2,300 inputs were fed to both one code point at a
time, comparing the full rule set at every step, plus whole-string parses,
`ParseState` string forms and `Graph.print()` output, plus 839 malformed and
randomly mutated grammars comparing error types and messages. Every case matched
except the one below.

## Known divergence from the reference

**Unbounded recursion** (a left-recursive rule such as `ba ::= bar | ba`, or an
empty repetition such as `("")+`) exhausts the stack as
`RangeError: Maximum call stack size exceeded` rather than Python's
`RecursionError`. This is the language-native equivalent, and matches the
behaviour the reference documents for its own upstream.
