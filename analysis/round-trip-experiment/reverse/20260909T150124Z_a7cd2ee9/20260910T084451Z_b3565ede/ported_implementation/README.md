# GBNF (Python)

A Python port of `reference_implementation/` (TypeScript) — a library for parsing
`.gbnf` grammars and incrementally validating input against them.

## Usage

```py
from gbnf import GBNF

state = GBNF('root ::= "foo"')   # ParseState
state = state.add("f")           # raises InputParseError on invalid input
state = state + "o"              # `+` is an alias for `add`
[*state]                         # [RuleChar(value=[111])]
```

`GBNF(grammar, initial_string="")` returns a `ParseState`. A `ParseState` is
immutable: `add()` returns a new state. Iterating a state yields the deduplicated
set of rules (`RuleChar`, `RuleCharExclude`, `RuleEnd`) that may come next.

Exports: `GBNF`, `GrammarParseError`, `InputParseError`, `RuleChar`,
`RuleCharExclude`, `RuleEnd`, `RuleType`, `ParseState`, `Graph`.

## Layout

The module layout mirrors the TypeScript source (file names are snake_cased):

| TypeScript                        | Python                    |
| --------------------------------- | ------------------------- |
| `src/gbnf.ts`                     | `gbnf/gbnf.py`            |
| `src/rules-builder/`              | `gbnf/rules_builder/`     |
| `src/grammar-parser/`             | `gbnf/grammar_parser/`    |
| `src/grammar-graph/`              | `gbnf/grammar_graph/`     |
| `src/utils/`                      | `gbnf/utils/`             |

## Tests

The suite in `tests/` is a copy of `/workspace/tests/python`, per that
directory's README.

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

`python -m pytest` puts the working directory on `sys.path`, which is how
`import gbnf` resolves; there is no install step.

## Notes on the port

- `char_at()` (`gbnf/rules_builder/char_at.py`) reproduces JavaScript's
  out-of-bounds string indexing, which the parser relies on: the TypeScript
  source compares `src[pos]` against a character at positions that may sit past
  the end of the grammar, and expects `undefined` rather than an error. `None`
  plays that role here.
- `RuleRef.nodes` is a list rather than a set. The TypeScript source uses a
  `Set`, which is insertion-ordered in JavaScript; a Python `set` is not, and
  rule iteration order is observable through `ParseState`.
- `parse_char` raises `GrammarParseError` for a malformed `\x`/`\u`/`\U` escape
  (e.g. `"\x"` at end of input), where the TypeScript source produces `NaN` and
  carries on with a rule that can never match.
