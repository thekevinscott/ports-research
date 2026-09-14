# gbnf (Python port)

A port of `reference_implementation/` (TypeScript) to Python. The module layout mirrors
the reference one-to-one, with names converted to `snake_case`:

| TypeScript                            | Python                                  |
| ------------------------------------- | --------------------------------------- |
| `src/GBNF.ts`                         | `gbnf/gbnf.py`                          |
| `src/grammar-graph/*.ts`              | `gbnf/grammar_graph/*.py`               |
| `src/grammar-parser/build-rule-stack.ts` | `gbnf/grammar_parser/build_rule_stack.py` |
| `src/rules-builder/*.ts`              | `gbnf/rules_builder/*.py`               |
| `src/utils/**/*.ts`                   | `gbnf/utils/**/*.py`                    |

## Usage

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add("f")   # or: state + "f"
list(state)              # [RuleChar([111])] -- the rules valid at this point
```

`GBNF` raises `GrammarParseError` for an invalid grammar and `InputParseError` for input
the grammar rejects.

## Tests

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

## Notes on the port

- `parse_char` reproduces JavaScript's `parseInt(str, 16)` for `\x`/`\u`/`\U` escapes,
  including its `NaN` result for a missing hex digit, so malformed escapes fail exactly
  where the reference fails.
- Indexing past the end of a string yields `undefined` in JavaScript and compares false;
  `rules_builder/char_at.py` provides the same behavior for the parser's lookaheads.
- `GraphPointer.resolve` and `GraphPointer.fetch_next` loop where the reference makes a
  tail call up a pointer's parent chain. That chain grows with each repetition of a
  `*`/`+` rule, and recursing on it would exhaust Python's much smaller stack on long
  runs of repeated input. The branching case (a rule reference fanning out over its
  nodes) stays recursive, so grammars that loop forever — an empty rule under a `+`, for
  instance — still fail fast rather than hanging.
