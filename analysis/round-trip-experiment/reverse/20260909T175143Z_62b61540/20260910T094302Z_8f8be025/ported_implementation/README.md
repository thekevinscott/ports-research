# gbnf

A Python port of `reference_implementation/` (the TypeScript `gbnf` package), a library for
parsing GBNF grammars.

## Usage

```py
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add("f")
print([*state])  # [RuleChar([111])]
```

`GBNF(grammar, initial_string="")` returns a `ParseState`. Iterating a `ParseState` yields the
set of rules (`RuleChar`, `RuleCharExclude`, `RuleEnd`) that may come next; `state.add(input)`
returns a new `ParseState` advanced by `input`, and raises an `InputParseError` if the input
cannot be parsed. An invalid grammar raises a `GrammarParseError`.

## Layout

Each module mirrors its counterpart in the TypeScript reference:

| Python | TypeScript |
| --- | --- |
| `gbnf/GBNF.py` | `src/GBNF.ts` |
| `gbnf/rules_builder/` | `src/rules-builder/` |
| `gbnf/grammar_parser/` | `src/grammar-parser/` |
| `gbnf/grammar_graph/` | `src/grammar-graph/` |
| `gbnf/utils/` | `src/utils/` |

Deviations, all of them mechanical:

- `state + "text"` is accepted as a synonym for `state.add("text")`.
- Reads past the end of the grammar string are routed through `utils/char_at.py`, which
  returns `""`. The reference relies on JavaScript's out-of-range read yielding `undefined`,
  which fails the comparison it is part of; in Python the same read raises `IndexError`.
- `RuleRef.nodes` is an insertion-ordered `list` rather than a `Set`, and
  `Graph._iterate_over_pointers` groups pointers in a dict keyed by `id(rule)` rather than by
  the rule object. Both preserve the reference's ordering and its
  identical-rules-are-distinct-if-distinct-objects behaviour.
- Rule classes compare by value (`RuleChar([102]) == RuleChar([102])`) but keep identity
  hashing, since the graph holds them in identity-keyed collections.
- Bare `throw new Error(...)` becomes `ValueError` (`TypeError` for the argument type checks
  in `GBNF`). `GrammarParseError` and `InputParseError` keep their names, their message
  formatting, and support `==`.
- Private `#fields` become single-underscore attributes, and names are snake_case;
  `RuleType`/`InternalRuleType` are `str` enums, so a rule's `type` still serializes as
  `"char"`, `"char_exclude"`, `"end"`.

## Tests

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest tests
```
