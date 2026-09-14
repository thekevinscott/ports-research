# gbnf — TypeScript port

A TypeScript port of `/workspace/reference_implementation` (the Python `gbnf` package),
module-for-module.

## Running the tests

`vitest` is installed globally in this environment and linked into `node_modules/`,
so no install step is needed:

```sh
cd /workspace/ported_implementation
npx vitest run --config vitest.config.unit.ts
```

`tests/` holds the generated suite copied verbatim from `/workspace/tests/javascript`,
plus `tests/port-extras/` — tests written for this port covering surface the generated
suite does not exercise (the graph printer, error accessors, escape sequences,
`ParseState.size`/`.grammar`, argument validation).

## Layout

Each Python module maps to a kebab-case TypeScript module with camelCase symbols:

| Python | TypeScript |
| --- | --- |
| `gbnf/GBNF.py` | `src/gbnf.ts` |
| `gbnf/__init__.py` | `src/index.ts` |
| `gbnf/rules_builder/` | `src/rules-builder/` |
| `gbnf/grammar_parser/` | `src/grammar-parser/` |
| `gbnf/grammar_graph/` | `src/grammar-graph/` |
| `gbnf/utils/` | `src/utils/` |

`GBNF` is both the default and a named export; `RuleType`, `RuleChar`,
`RuleCharExclude`, `RuleEnd`, `GrammarParseError` and `InputParseError` are named
exports.

## Intentional divergences from the reference

Both are cases where the Python reference does not behave the way the test suite
requires. Everything else was verified identical by differential testing: across a
corpus of grammar/input pairs the two implementations produce the same set of rules
and byte-identical error messages.

1. **Rule ordering is insertion order.** `RuleRef.nodes` is a Python `set` in the
   reference, so iterating it yields rules in an arbitrary (id-hash) order. This port
   uses a JS `Set`, which preserves insertion order. The generated suite depends on
   this: for `root ::= ( [^abcdefgh] | [b-z])*` the reference yields
   `[end, char_exclude, char]` while the suite requires `[char_exclude, char, end]`.

2. **Rules carry a `type` field.** Python's `Rule` classes expose their type only via
   a `__dict__` property, so `Graph.print()` in the reference raises
   `AttributeError: 'RuleEnd' object has no attribute 'type'` for every grammar. Here
   the rule classes have a real `type` field (`'char'`, `'char_exclude'`, `'end'`,
   `'rule_ref'`), which both fixes `print()` and gives the shape the suite asserts
   against (`{ type: 'char', value: [102] }`).
