# GBNF (Python)

A Python port of `reference_implementation/` (the TypeScript `gbnf` package): a library
for parsing `.gbnf` grammars and walking the resulting grammar graph.

## Usage

```py
from gbnf import GBNF, InputParseError, GrammarParseError

state = GBNF('root ::= "foo"')
state = state.add("f")
print([*state])  # [RuleChar(value=[111])]
```

`GBNF(grammar, initial_string="")` returns a `ParseState`, which is iterable over the
rules that may come next (`RuleChar`, `RuleCharExclude`, `RuleEnd`), exposes `size` and
`grammar`, and returns a new `ParseState` from `add(text)` (also spelled `state + text`).
Invalid grammars raise `GrammarParseError`; input that the grammar cannot accept raises
`InputParseError`.

## Layout

The module structure mirrors the TypeScript package one-to-one (kebab-case files become
snake_case, camelCase functions become snake_case):

| TypeScript | Python |
| --- | --- |
| `src/GBNF.ts` | `gbnf/GBNF.py` |
| `src/grammar-graph/` | `gbnf/grammar_graph/` |
| `src/grammar-parser/` | `gbnf/grammar_parser/` |
| `src/rules-builder/` | `gbnf/rules_builder/` |
| `src/utils/` | `gbnf/utils/` |

## Tests

The generated suite from `tests/python` is copied into `tests/`:

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

## Notes on the port

- **Rule equality**: `RuleChar`, `RuleCharExclude` and `RuleEnd` compare by type and
  value, but keep the identity `__hash__`, because the graph keys rules and nodes by
  reference the way the TypeScript `Map`/`Set` do.
- **Ranges** are two element `list`s (not tuples), matching the JSON-ish shape the
  TypeScript rules use.
- **Reading past the end of the grammar**: JavaScript yields `undefined` when indexing
  out of bounds, where Python raises `IndexError`. `char_at` in `rules_builder.py`
  restores the JS behavior, so an unterminated `"` string or `[` char class still raises
  the `GrammarParseError` that `parse_char` defines.
- **Rule ordering**: `RuleRef.nodes` is an insertion-ordered `list` (deduped), matching
  the reference's ordered `Set`, so alternate paths are yielded in grammar order.
