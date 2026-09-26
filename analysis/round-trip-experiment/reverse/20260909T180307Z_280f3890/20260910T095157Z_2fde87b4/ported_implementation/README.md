# GBNF (Python)

A library for parsing `.gbnf` grammar files, ported from the TypeScript implementation in
`../reference_implementation`.

## Usage

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
for rule in state:
    ...            # RuleChar([102])

state = state.add("f")   # returns a new ParseState; `state + "f"` is equivalent
state.size               # number of distinct rules reachable now
state.grammar            # the source grammar
```

`GBNF(grammar, initial_string="")` returns a `ParseState`. A `ParseState` is iterable and
yields the distinct `RuleChar` / `RuleCharExclude` / `RuleEnd` rules that could match next.
Invalid grammars raise `GrammarParseError`; input the grammar cannot accept raises
`InputParseError`.

## Layout

The module layout mirrors the TypeScript source, with file names snake_cased:

| TypeScript                               | Python                                    |
| ---------------------------------------- | ----------------------------------------- |
| `src/gbnf.ts`                            | `gbnf/GBNF.py`                            |
| `src/rules-builder/`                     | `gbnf/rules_builder/`                     |
| `src/grammar-parser/build-rule-stack.ts` | `gbnf/grammar_parser/build_rule_stack.py` |
| `src/grammar-graph/`                     | `gbnf/grammar_graph/`                     |
| `src/utils/`                             | `gbnf/utils/`                             |

## Tests

`tests/` is a copy of the generated suite in `../tests/python` — 773 cases.

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

## Notes on the port

- **Indexing.** JavaScript strings index by UTF-16 code unit and return `undefined` past the
  end; Python indexes by code point and raises. `parse_char` therefore always advances by one
  position (the TypeScript version advances by two for astral characters), and the rules
  builder reads through a `_char_at` helper that yields `None` out of bounds, preserving the
  reference's error paths.
- **`parseInt` semantics.** `parse_char._parse_int_hex` reproduces `Number.parseInt(s, 16)`,
  which reads the longest leading run of hex digits and ignores the rest, rather than
  `int(s, 16)`, which rejects trailing garbage.
- **Rule identity.** `Graph` dedupes rules by serialized key and then keys pointers by rule
  identity, matching the reference's use of a `Map` with object keys; the Python version uses
  `id(rule)` for that map.
- **Errors** compare equal when their rendered messages match, which is what the test suite
  asserts.

Equivalence was checked differentially against the TypeScript reference over the grammar
fixtures plus 35 hand-written edge-case grammars and 39 input strings, exercising both the
initial-string and incremental `add` paths: 3354 comparison points, all byte-identical.
