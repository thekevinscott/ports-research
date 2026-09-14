# gbnf (Python port)

A Python port of `reference_implementation/` — the Javascript `gbnf` library for
parsing GBNF grammars.

## Usage

```python
from ported_implementation import GBNF

state = GBNF('root ::= "yes" | "no"')
for rule in state:
    print(rule)
    # RuleChar(value=[121], type=<RuleType.CHAR: 'char'>)   # "y"
    # RuleChar(value=[110], type=<RuleType.CHAR: 'char'>)   # "n"
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`state` is iterable (`list(state)`, `[*state]`) and can also be iterated through
`state.rules()`. States are *immutable*; to parse more input call `state.add()`,
which returns a new state:

```python
state = GBNF('root ::= "I like green eggs and ham"')
print(list(state))     # [RuleChar(value=[73])]   # "I"
state = state.add("I li")
print(list(state))     # [RuleChar(value=[107])]  # "k"
state = state.add("ke gree")
print(list(state))     # [RuleChar(value=[110])]  # "n"
```

`state("...")` is a shorthand for `state.add("...")`. Input that the grammar
cannot accept raises `InputParseError`.

The rules returned are:

- `RuleChar` — `value` holds code points to match, where an entry may itself be a
  `[start, end]` range.
- `RuleCharExclude` — the same, for code points that must *not* match.
- `RuleEnd` — a valid end of the string.

Rules expose `.type` and `.value`, compare by value, and can also be read as
mappings (`rule["type"]`, `dict(rule)`) so they interoperate with dict-shaped
expectations.

## Layout

The module layout mirrors the reference one-to-one, so the two can be read side by
side:

| reference (`src/`)                | port                              |
| --------------------------------- | --------------------------------- |
| `gbnf.ts`                         | `gbnf.py`                         |
| `rules-builder/*.ts`              | `rules_builder/*.py`              |
| `grammar-parser/build-rule-stack` | `grammar_parser/build_rule_stack` |
| `grammar-graph/*.ts`              | `grammar_graph/*.py`              |
| `utils/**/*.ts`                   | `utils/**/*.py`                   |

Names are snake_cased; where the reference exported a camelCase name, that spelling
is kept as an alias (`is_range`/`isRange`) so either spelling works.

## Tests

```bash
python3 ported_implementation/run_tests.py      # or: pytest ported_implementation/tests
```

- `tests/test_gbnf.py` — behaviour of the public API.
- `tests/test_parity.py` — replays `tests/cases.py` (hand-written cases plus seeded
  random grammars from `tests/fuzz.py`) and asserts the port produces exactly what
  the reference implementation produced, as recorded in
  `tests/fixtures/reference.json`.

The fixtures were recorded by running the reference Typescript itself under Node's
type-stripping mode:

```bash
python3 ported_implementation/tools/record_reference.py   # needs node >= 22.6
```

Re-run that after changing `tests/cases.py` or the fuzz seed. Node is only needed
to record fixtures, not to run the tests.

Beyond the committed corpus, the port was checked against the reference on 1652
additional randomly generated grammar/input pairs (fuzz seeds 1, 2, 3, 5, 8, 13, 21)
with no divergence.

## Deviations from the reference

Three places where matching the reference exactly would be wrong in Python:

1. **Non-BMP characters.** Javascript strings are UTF-16, so the reference splits
   characters above `U+FFFF` into surrogate halves — `GBNF('root ::= "😀"')` matches
   only the lead surrogate, and feeding `"😀"` as input never matches an escape like
   `\U0001F600`. Python strings are sequences of code points, and the port treats
   them as such, so astral characters work in both grammars and input.
2. **Infinite recursion.** A grammar that can expand forever (`root ::= a*` with
   `a ::= "b"?`, or `root ::= root`) makes the reference exhaust the Javascript call
   stack and throw `RangeError`. The port walks the graph iteratively, so it instead
   enforces an explicit depth bound (`grammar_graph.graph_pointer.MAX_POINTER_DEPTH`)
   and raises `RecursionError`. The bound is far above what real grammars use — rule
   reference chains thousands deep still parse, where the recursive reference and a
   recursive port would both fall over.
3. **Missing `root` symbol.** The reference's check for a missing root symbol
   (`symbolIds.get('root') === undefined`) is unreachable, because its `SymbolIds.get`
   throws on a missing key first; the intended `GrammarParseError` never surfaces. The
   port raises that intended error, listing the symbols the grammar does define.

Two smaller notes:

- `src/builder/` is imported by `gbnf.ts` but is not part of the provided reference
  snapshot, so the builder API is not ported. `GBNF()` accepts a string, or any
  object whose `str()` is the grammar.
- An invalid hex escape (`"\x"` with no digits) yields `NaN` in the reference, which
  silently matches nothing. The port raises `GrammarParseError` instead.
