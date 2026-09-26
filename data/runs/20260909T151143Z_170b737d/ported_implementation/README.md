# GBNF (TypeScript port)

A TypeScript port of `reference_implementation/` — a library for parsing `.gbnf`
grammar files.

```ts
import { GBNF } from "gbnf";

let state = GBNF('root ::= "foo"');
[...state]; // [ RuleChar { value: [ 102 ] } ]  — the characters accepted next
state = state.add("f");
[...state]; // [ RuleChar { value: [ 111 ] } ]
```

## Layout

The module tree mirrors the Python package one-to-one, so each file can be diffed
against its counterpart:

| Python | TypeScript |
| --- | --- |
| `gbnf/__init__.py` | `src/index.ts` |
| `gbnf/GBNF.py` | `src/GBNF.ts` |
| `gbnf/grammar_graph/*.py` | `src/grammar_graph/*.ts` |
| `gbnf/grammar_parser/*.py` | `src/grammar_parser/*.ts` |
| `gbnf/rules_builder/*.py` | `src/rules_builder/*.ts` |
| `gbnf/utils/**/*.py` | `src/utils/**/*.ts` |

Function, method and attribute names are kept identical to the reference
(`parse_space`, `build_rule_stack`, `previous_code_points`, `__roots__`, …) so
the two implementations read side by side. `src/utils/python_compat.ts` is the
one addition: it holds the few Python runtime behaviours the port has to
reproduce explicitly (`KeyError`, `IndexError`, string subscript bounds
checking, and `json.dumps`' `", "` separators).

## Running

Requires Node 22.18+ (the port is executed directly via Node's built-in
TypeScript type stripping — no build step, no dependencies).

```bash
npm test                              # unit tests + parity tests
python3 tests/parity/generate_fixtures.py   # re-record the reference's behaviour
```

`npm test` also picks up anything in the repository's top-level `tests/`
directory if it is populated.

## Tests

* `tests/unit/` — ported from the reference's own `*_test.py` suites.
* `tests/parity/` — a differential suite. `generate_fixtures.py` runs the Python
  reference over 29 grammars (including the arithmetic, JSON and Japanese
  grammars) plus 12 invalid ones, recording rule tables, symbol ids, stacked
  rules, and — for a 24-step walk in two directions — the rules exposed at each
  step, the code point chosen from them, and any error message.
  `parity.test.ts` replays the identical driver against this port and asserts
  every recorded value still matches.

## Notes on fidelity

Behaviour is preserved even where the reference is surprising:

* `Graph.print()` raises for `RuleEnd`/`RuleCharExclude` nodes. The Python
  `Rule` classes expose `type` only through their `__dict__` property, so
  `rule.type` raises `AttributeError`; the port raises the same way rather than
  silently printing `undefined`.
* A grammar without a `root` rule raises `KeyError('root')`, not the
  `GrammarParseError` the surrounding code appears to intend — `SymbolIds`
  subscripting raises before the `is None` check can run.
* `Graph.__iterate_over_pointers__` seeds each rule's group with its first
  pointer and then appends that pointer again, so single-pointer groups hold two
  entries.
* `Graph`'s `unique_rules` map is written and read back in the same step, so the
  intended de-duplication of identical rules is a no-op.

Two places where the port necessarily differs:

* **Rule ordering is deterministic here.** `RuleRef.nodes` is a Python `set` of
  identity-hashed nodes, so the reference yields the rules for a given parse
  state in an order that changes between processes. The port uses an
  insertion-ordered `Set`, which yields them in grammar order. The parity suite
  therefore compares rule *sets*, sorted on both sides.
* **String indices are UTF-16.** Python indexes strings by code point. Where
  that matters — `parse_char` reading a literal astral character — the port
  reads the whole code point and advances by two UTF-16 units, which is the
  equivalent step. Error-position columns for grammars containing literal astral
  characters can therefore differ by one per such character.
