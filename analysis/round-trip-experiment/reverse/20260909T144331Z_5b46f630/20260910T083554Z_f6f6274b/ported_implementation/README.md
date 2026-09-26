# GBNF (Python)

A Python port of `reference_implementation/` — a library for parsing `.gbnf` grammar files
and incrementally validating input against them.

## Usage

```py
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add('f')

for rule in state:
    ...  # RuleChar / RuleCharExclude / RuleEnd describing what may come next
```

`GBNF(grammar, initial_string='')` returns a `ParseState`. A `ParseState` is iterable (it
yields the rules that could match next), exposes `size` and `grammar`, and `add(text)`
returns a new `ParseState`. `state + text` is an alias for `state.add(text)`, and
`len(state)` / `bool(state)` are backed by `size`. Invalid grammars raise
`GrammarParseError`; invalid input raises `InputParseError`.

## Layout

The module layout mirrors the TypeScript reference one-to-one, with `camelCase` filenames
renamed to `snake_case`:

| reference (TypeScript)          | port (Python)                 |
| ------------------------------- | ----------------------------- |
| `src/GBNF.ts`                   | `gbnf/GBNF.py`                |
| `src/rulesBuilder/`             | `gbnf/rules_builder/`         |
| `src/grammarParser/`            | `gbnf/grammar_parser/`        |
| `src/grammarGraph/`             | `gbnf/grammar_graph/`         |
| `src/utils/`                    | `gbnf/utils/`                 |

Methods keep their reference behaviour under `snake_case` names (`fetchNext` →
`fetch_next`, `toDict` → `to_dict`), and the private `#field` members become `_field`.

## Tests

```sh
cd /workspace/ported_implementation
cp -r /workspace/tests/python tests
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

All 773 cases pass. `tests/` is the generated Python suite copied verbatim from
`/workspace/tests/python`, grammar fixtures included.

## Notes on the translation

- **String indexing.** JavaScript strings index by UTF-16 code unit, Python strings by code
  point, and the reference's positions are code-point based. That makes
  `gbnf/utils/code_point_length.py` a plain `len()` here, and `parse_char` always reports a
  width of `1` for an unescaped character rather than `2` for one outside the Basic
  Multilingual Plane.
- **Out-of-range indexing.** Reading past the end of a JavaScript string yields `undefined`
  rather than raising, and the scanner relies on that in several places (the unterminated
  `"…` and `[…` loops, the `\r\n` lookahead, the `-` range lookahead, the `)` check, and
  the escape character in `parse_char`). `gbnf/rules_builder/char_at.py` reproduces it.
- **Ordered collections.** `Map` and insertion-ordered `Set` map onto `dict`, so `Pointers`,
  `SymbolIds` and the graph's root/rule bookkeeping preserve the reference's ordering — the
  order rules are yielded in is identical.
- **Identity vs. value semantics.** `Graph._iterate_over_pointers` groups pointers by rule
  *object*, matching the reference's `Map` keyed on a rule reference; since the rule classes
  here define `__eq__`, that grouping is keyed on `id(rule)` explicitly. Likewise
  `RuleRef.nodes` de-duplicates graph nodes by identity, as `new Set(...)` does.
- **Errors.** `GrammarParseError` and `InputParseError` are `Exception` subclasses whose
  `__str__` reproduces the reference's message verbatim, and whose `__eq__` compares those
  messages — the reference's `equals`. The reference's plain `Error` throws for programmer
  mistakes become `ValueError`.
- **Rule instances carry only `value`.** The `type` discriminator is a property rather than
  an attribute, so `RuleEnd().__dict__` is `{}` and `RuleChar([...]).__dict__` is
  `{'value': [...]}`, which the test suite sorts on.
- `gbnf/utils/validate_non_empty.py` is carried over from the reference, where it is unused.

## Verification

Beyond the test suite, a differential harness ran both implementations over 41,124
(grammar, input) combinations — every grammar under `tests/iteration/grammars/` plus inline
grammars, breadth-first over input prefixes — comparing rule lists, rule order, `size`, and
error messages. It additionally compared 44 malformed grammars, 45 incremental `add()`
sequences (including `error_for_most_recent_input` and `src`), and `Graph.print()` output
with and without colour. All results were identical.
