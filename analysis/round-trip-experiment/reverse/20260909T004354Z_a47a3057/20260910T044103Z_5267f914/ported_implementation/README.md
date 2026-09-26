# gbnf — Python port

A Python port of `/workspace/reference_implementation` (the TypeScript `gbnf` package),
module-for-module.

## Running the tests

`pytest` comes from `uv`'s offline cache, so no install step is needed:

```sh
cd /workspace/ported_implementation
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

`tests/` holds the generated suite copied verbatim from `/workspace/tests/python`.
`python -m pytest` puts the working directory on `sys.path`, so `import gbnf` resolves
from the port root.

## Layout

Each TypeScript module maps to a snake_case Python module with snake_case symbols:

| TypeScript | Python |
| --- | --- |
| `src/gbnf.ts` | `gbnf/GBNF.py` |
| `src/index.ts` | `gbnf/__init__.py` |
| `src/rules-builder/` | `gbnf/rules_builder/` |
| `src/grammar-parser/` | `gbnf/grammar_parser/` |
| `src/grammar-graph/` | `gbnf/grammar_graph/` |
| `src/utils/` | `gbnf/utils/` |

`GBNF`, `RuleType`, `RuleChar`, `RuleCharExclude`, `RuleEnd`, `ParseState`, `Graph`,
`GrammarParseError` and `InputParseError` are exported from the `gbnf` package.

Class members named `#foo` in TypeScript become `_foo`; getters and setters become
`@property`. Generators (`GraphPointer.resolve`, `Graph._resolve_pointer`,
`ParseState.rules`, …) stay generators. `ParseState` is iterable via `__iter__`, and
`state + text` is `state.add(text)`.

## Notes on the translation

These are the places where matching the reference's behaviour took more than a
mechanical rename. Behaviour was verified by differential testing: across the grammar
corpus plus a set of edge-case grammars (unterminated strings and classes, bad escapes,
missing `root`, astral-plane input, comments) the two implementations produce identical
rule sets, identical `Graph.print()` output — plain and colorized — identical symbol-id
tables and byte-identical error messages over 23k incremental parse steps.

1. **Out-of-bounds indexing.** Indexing a JavaScript string past its end yields
   `undefined` rather than raising, and the reference's parser relies on that: the
   string- and char-class loops in `RulesBuilder.parse_sequence` run past the end of the
   grammar and let `parse_char` raise the "Unexpected end of grammar input" error.
   `rules_builder.char_at` reproduces it by returning `None`.

2. **Insertion-ordered rule references.** `RuleRef.nodes` is a JS `Set`, which iterates
   in insertion order; it is a `list` here, since a Python `set` would expose rules in an
   arbitrary order and the suite depends on the order (for
   `root ::= ( [^abcdefgh] | [b-z])*` it requires `[char_exclude, char, end]`).
   `Pointers` and `SymbolIds` likewise rely on `dict` preserving insertion order, as the
   JS `Map`s they port do — including the rule that re-assigning an existing key keeps
   its original position.

3. **Identity-keyed rule grouping.** `Graph._iterate_over_pointers` groups pointers by
   rule *identity*, as the reference's `Map` keyed on object reference does, so it keys
   on `id(rule)`. The rule classes carry a value-based `__eq__` (the suite compares rules
   against expected `RuleChar`/`RuleEnd` instances), which would otherwise collapse
   distinct-but-equal rules into one group.

4. **`type` is an instance attribute.** The suite sorts rules by
   `json.dumps(rule.__dict__)`, so `type` has to be in each rule's instance `__dict__`
   (`{"type": "char", "value": [102]}`), not a class attribute.

5. **Error equality.** `GrammarParseError` and `InputParseError` compare equal by
   rendered message, so an error raised internally with a list of code points equals the
   test's expectation built from the equivalent string.

6. **Code points, not UTF-16.** `build_error_position` uses `len()` directly; the
   reference needs an explicit `Array.from(...).length` to get the same column for
   astral-plane input.

7. **Type errors.** The reference's argument checks throw a plain `Error`; here they
   raise `TypeError` (e.g. `GBNF(5)` → `TypeError: grammar must be a string`). Checks
   that signal a corrupt graph or grammar raise `ValueError`.
