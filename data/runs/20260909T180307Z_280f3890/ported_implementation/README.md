# GBNF (TypeScript)

A library for parsing `.gbnf` grammar files, ported from the Python implementation in
`../reference_implementation`.

## Usage

```ts
import { GBNF } from 'gbnf';

let state = GBNF('root ::= "foo"');
for (const rule of state) {
  // { type: 'char', value: [102] }
}

state = state.add('f');   // returns a new ParseState
state.size;               // number of distinct rules reachable now
state.grammar;            // the source grammar
```

`GBNF(grammar, initialString?)` returns a `ParseState`. A `ParseState` is iterable and yields
the distinct `RuleChar` / `RuleCharExclude` / `RuleEnd` rules that could match next. Invalid
grammars throw `GrammarParseError`; input that the grammar cannot accept throws
`InputParseError`.

## Layout

The module layout mirrors the Python package, with file names kebab-cased:

| Python                                  | TypeScript                             |
| --------------------------------------- | -------------------------------------- |
| `gbnf/GBNF.py`                          | `src/gbnf.ts`                          |
| `gbnf/rules_builder/`                   | `src/rules-builder/`                   |
| `gbnf/grammar_parser/build_rule_stack.py` | `src/grammar-parser/build-rule-stack.ts` |
| `gbnf/grammar_graph/`                   | `src/grammar-graph/`                   |
| `gbnf/utils/`                           | `src/utils/`                           |

## Tests

`tests/` is a port of the generated Python suite in `../tests/python` — the same 773 cases,
case for case. The grammar fixtures under `tests/iteration/grammars/` are copied verbatim.

```sh
vitest run
```

`vitest` is installed globally in this image; there is no `node_modules` here because the npm
registry is unreachable. In a normal checkout, `npm install && npm test` does the same thing.
`npm run typecheck` needs `typescript`, which is likewise not installable offline.

## Notable differences from the Python reference

These are the only places where the port does not reproduce the reference exactly. All three
are cases where the Python code raises an *unintended* built-in exception; the port raises the
domain error the surrounding code clearly intends. They are unreachable from the test suite.

1. **Missing `root` symbol.** `GBNF.py` does `symbol_ids["root"] is None`, which raises
   `KeyError` when the grammar defines rules but no `root` (e.g. `foo ::= "bar"`). The port
   throws `GrammarParseError(..., "Grammar does not contain a 'root' symbol")`.
2. **Parser reads past the end of the grammar.** Python indexing raises `IndexError` for an
   unterminated group with no trailing newline (e.g. `root ::= ([a-z]`); JS returns `undefined`
   and the existing checks then throw `GrammarParseError(..., "Expecting ')' at 15")`.
3. **Error position at the very end of the input.** `build_error_position` walks
   `lines[line_idx]` past the end of the list and raises `IndexError` when the failing position
   is the last character of the last line. The port stops at the end of the list and renders a
   normal `InputParseError` message.

Two smaller notes:

- Rules are modelled as classes with a `type` discriminator (`'char'`, `'char_exclude'`,
  `'end'`, `'ref'`) rather than Python dataclasses. `print.ts` reads `rule.type`, which the
  Python `print.py` also does — but there it is an `AttributeError`, since `Rule` has no such
  attribute.
- `utils/validate_non_empty.py` is not ported. In Python it is only referenced from
  `dataclasses.field(metadata=...)`, which never runs it, so it has no behaviour to port.

Equivalence was checked differentially against the Python reference over the grammar fixtures
plus hand-written edge-case grammars and 71 input strings: 2723 comparison points, 2666
byte-identical, and the remaining 57 were the Python crashes described above.
