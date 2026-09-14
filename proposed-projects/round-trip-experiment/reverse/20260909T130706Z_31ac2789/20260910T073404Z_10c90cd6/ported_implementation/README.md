# GBNF (Python)

A Python port of `reference_implementation/` — a library for parsing `.gbnf` grammar files.

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add('f')          # or: state = state + 'f'

for rule in state:
    ...  # RuleChar(value=[111]) — the characters that may come next
```

## Layout

The port mirrors the TypeScript reference file for file:

| TypeScript | Python |
| --- | --- |
| `src/gbnf.ts` | `gbnf/GBNF.py` |
| `src/rules_builder/*` | `gbnf/rules_builder/*` |
| `src/grammar_parser/build_rule_stack.ts` | `gbnf/grammar_parser/build_rule_stack.py` |
| `src/grammar_graph/*` | `gbnf/grammar_graph/*` |
| `src/utils/*` | `gbnf/utils/*` |

`gbnf/__init__.py` re-exports the whole public surface. Identifiers are snake_case
(`parse_char`, `build_rule_stack`, `get_serialized_rule_key`), and every function is
additionally exported under its TypeScript name (`parseChar`, `buildRuleStack`, …) so code
written against the reference's names keeps working.

## Tests

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

`tests/` is the generated suite from `/workspace/tests/python`.

## Differences from the TypeScript reference

Behaviour is identical — the port reproduces the reference's rules, symbol ids, rule stacks,
parse states and error messages exactly, including the order rules come out of a parse state.
The differences are the ones the language forces:

1. **Positions are code point based.** Python strings are indexed by code point rather than
   UTF-16 code unit, so `parse_char` reports a literal astral character (an emoji, say) as one
   character one position wide, where the reference reports two. Everything in the BMP, and
   every error message column, is unchanged.
2. **`get_serialized_rule_key`** uses `json.dumps`, so it emits `1-[[97, 122]]` where
   `JSON.stringify` emits `1-[[97,122]]`. The key is only used to compare rules internally.
3. **`ParseState`.** `state.add(text)` is joined by `state + text`; iteration
   (`for rule in state`), `state.size` (also `len(state)`) and `state.grammar` are unchanged.
4. **Errors** are raised as `GrammarParseError` / `InputParseError`, both plain `Exception`
   subclasses, and compare equal to another instance describing the same failure.
