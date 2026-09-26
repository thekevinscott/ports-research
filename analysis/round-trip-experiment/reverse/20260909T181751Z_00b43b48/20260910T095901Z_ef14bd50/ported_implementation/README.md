# GBNF (Python)

A Python port of `reference_implementation/` (the TypeScript `gbnf` package): a library for
parsing `.gbnf` grammar files and walking the resulting grammar graph.

## Usage

```py
from gbnf import GBNF

state = GBNF('root ::= "foo" | "bar"')
state = state.add("b")
[*state]  # [RuleChar([97])]
```

`GBNF(grammar, initial_string="")` returns a `ParseState`, which is iterable over the set of rules
that may come next. `state.add(text)` returns a new `ParseState` advanced by `text` (`state + text`
is a synonym), and raises an `InputParseError` if the text cannot be parsed. An invalid grammar
raises a `GrammarParseError`.

Exports: `GBNF`, `ParseState`, `Graph`, `RuleType`, `RuleChar`, `RuleCharExclude`, `RuleEnd`,
`RuleRef`, `GrammarParseError`, `InputParseError`.

## Layout

The module structure mirrors the TypeScript source, with `kebab-case` files renamed to
`snake_case` and identifiers to `snake_case`:

| TypeScript | Python |
| --- | --- |
| `src/GBNF.ts` | `gbnf/GBNF.py` |
| `src/rules-builder/` | `gbnf/rules_builder/` |
| `src/grammar-parser/` | `gbnf/grammar_parser/` |
| `src/grammar-graph/` | `gbnf/grammar_graph/` |
| `src/utils/` | `gbnf/utils/` |

JS protocol methods map to their Python equivalents: `[Symbol.iterator]` → `__iter__`, `size` →
`__len__` (kept alongside a `size` property), `#privateFields` → name-mangled `__attrs__`.

## Tests

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

## Notes on the port

JavaScript semantics that have no direct Python equivalent are reproduced explicitly rather than
left to differ:

- **Out-of-bounds indexing.** `src[pos]` yields `undefined` in JS but raises `IndexError` in
  Python. `rules_builder.char_at()` restores the JS behaviour at each site where the reference
  relies on it (unterminated `"..."`, `[...]` and `(...)` groups reach the reference's own error
  paths instead of crashing).
- **Ordered collections.** `RuleRef.nodes` is a JS insertion-ordered `Set`; a Python `set` is
  unordered, so it is a `list` here, keeping the rules yielded by a `ParseState` in grammar order.
  `Map` becomes `dict`, which is insertion-ordered.
- **Rule identity.** `Graph` groups pointers by rule object identity (`Map` keyed by object). Since
  the rule classes define `__eq__`, the equivalent dicts are keyed by `id(rule)` rather than by the
  rule itself.
- **Code points.** JS `charCodeAt` returns UTF-16 code units; Python `ord()` returns full code
  points. They agree for everything in the Basic Multilingual Plane, which is what the grammars use,
  and `ord()` matches the per-code-point walk `getInputAsCodePoints` already performs.
