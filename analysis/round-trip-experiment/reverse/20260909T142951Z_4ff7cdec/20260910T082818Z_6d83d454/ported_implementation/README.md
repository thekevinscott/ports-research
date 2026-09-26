# GBNF

A library for parsing GBNF grammars, ported to Python from the TypeScript
reference implementation in `../reference_implementation`.

## Usage

```py
from gbnf import GBNF

state = GBNF('root ::= "foo"')
print([*state])  # [RuleChar([102])]

state = state.add('f')
print([*state])  # [RuleChar([111])]
```

`GBNF(grammar, initial_string='')` returns a `ParseState`. A `ParseState` is
iterable, and yields the deduplicated set of rules (`RuleChar`,
`RuleCharExclude`, `RuleEnd`) that the grammar permits at the current position.
`ParseState.add(text)` — also spelled `state + text` — returns a new
`ParseState` advanced by `text`, and raises an `InputParseError` if the text
cannot be parsed. An invalid grammar raises a `GrammarParseError`.

## Layout

The module layout mirrors the reference implementation:

| TypeScript                       | Python                  |
| -------------------------------- | ----------------------- |
| `src/gbnf.ts`                    | `gbnf/gbnf.py`          |
| `src/rules-builder/`             | `gbnf/rules_builder/`   |
| `src/grammar-parser/`            | `gbnf/grammar_parser/`  |
| `src/grammar-graph/`             | `gbnf/grammar_graph/`   |
| `src/utils/`                     | `gbnf/utils/`           |

Differences worth noting:

- The `Map`s backing `SymbolIds`/`Pointers` become `dict`s, which preserve
  insertion order the same way `Map` does.
- `RuleRef.nodes` is a list of nodes in path order rather than a `Set`, since
  Python's `set` is unordered and pointer resolution — and therefore the order
  rules are yielded in — has to stay deterministic.
- Rules keep the `type` discriminator (`'char'`, `'char_exclude'`, `'end'`,
  `'ref'`) as an instance attribute, so `__dict__` round-trips through `json`.
- `undefined` becomes `None`, and the TypeScript code's `throw new Error`
  becomes `raise ValueError`. Indexing a string past its end yields `None` via a
  `_char_at` helper, matching the reference's `undefined`.
- `Graph._iterate_over_pointers` groups pointers by `id(rule)` to keep the
  reference's identity-keyed `Map` semantics, which value-based `__eq__` on
  rules would otherwise change.
- Errors compare equal by their identifying fields (`GrammarParseError`) or by
  their normalized input and position (`InputParseError`).

## Tests

The generated suite from `/workspace/tests/python` is copied into `tests/`:

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```
