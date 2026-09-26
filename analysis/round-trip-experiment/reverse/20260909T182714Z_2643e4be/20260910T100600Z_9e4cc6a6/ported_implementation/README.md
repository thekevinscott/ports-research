# GBNF (Python port)

A Python port of `reference_implementation/` (the TypeScript `gbnf` package), a
library for parsing `.gbnf` grammars.

```py
from gbnf import GBNF

state = GBNF('root ::= "yes" | "no"')
state = state.add("y")
[*state]   # [RuleChar(value=[101])] — the rules that may come next
state.size # 1
```

## Layout

The module layout mirrors the reference one-to-one (file names are
snake_cased, identifiers are snake_cased; classes keep their names):

| TypeScript                               | Python                                    |
| ---------------------------------------- | ----------------------------------------- |
| `src/GBNF.ts`                            | `gbnf/GBNF.py`                            |
| `src/rules-builder/*.ts`                 | `gbnf/rules_builder/*.py`                 |
| `src/grammar-parser/build-rule-stack.ts` | `gbnf/grammar_parser/build_rule_stack.py` |
| `src/grammar-graph/*.ts`                 | `gbnf/grammar_graph/*.py`                 |
| `src/utils/**.ts`                        | `gbnf/utils/**.py`                        |

## Tests

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest tests
```

## Porting notes

Behaviour matches the reference exactly, including its quirks (`RulesBuilder`'s
time limit is measured in seconds; `Graph` accumulates `previous_code_points`
across `add` calls so error positions grow with the input; identical rules are
not de-duplicated in `Graph`).

Language differences that needed a decision:

- **Python builtins.** The reference defines `ValueError`, `KeyError` and
  `IndexError` classes in `src/utils/errors/python-errors.ts` to stand in for
  the builtins of the same names, and a `charAt` helper reproducing Python's
  out-of-bounds string indexing. Here they are the builtins again: `src[pos]`
  raises `IndexError` on its own, so a grammar with an unterminated string
  literal raises `IndexError`, and a grammar without a `root` rule raises
  `KeyError('root')` from the `symbol_ids["root"]` lookup in `GBNF.py` (which
  makes the "Grammar does not contain a 'root' symbol" branch below it
  unreachable, exactly as in the reference). Likewise `int(text, 16)` replaces
  the reference's `parseHex`.
- **Dunder methods.** `equals()` becomes `__eq__`, `toString()` becomes
  `__str__`, and `toDict()` becomes `__dict__` (a property, so — as in the
  reference's `toDict` — it reports the rule's class name under `"type"`).
  `ParseState.add(text)` is also reachable as `state + text` and
  `state(text)`; `state.size` and `len(state.pointers)` replace the `size`
  getters.
- **Iteration and ordering.** JavaScript `Map`s become dicts (both keep
  insertion order) and `Set`s become sets. `RuleRef.nodes` is a set, so the
  order in which pointers — and therefore the rules yielded by `ParseState` —
  come out after resolving a reference is not stable; compare them as an
  unordered collection.
- **Strings.** Python strings are sequences of code points, so
  `get_input_as_code_points` and `build_error_position` measure input in code
  points without the reference's `Array.from` dance. Grammar *text* is indexed
  by code point rather than UTF-16 code unit; that only differs for a literal
  non-BMP character written directly into a grammar (`\U0001F600` escapes are
  unaffected).
- **Rule identity.** `Graph._iterate_over_pointers` groups pointers by rule
  identity, as the reference's `Map` does; it keys on `id(rule)` because
  `__eq__` on rules compares by value.
