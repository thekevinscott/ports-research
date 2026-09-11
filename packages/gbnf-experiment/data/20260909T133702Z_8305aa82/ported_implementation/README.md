# GBNF

A library for parsing `.gbnf` grammar files in Python. This is a port of the
TypeScript reference implementation in `../reference_implementation`.

## Usage

Pass your grammar to `GBNF`:

```python
from gbnf import GBNF

state = GBNF('''
root  ::= "yes" | "no"
''')
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```python
from gbnf import GBNF

state = GBNF('''
root  ::= "yes" | "no"
''')
for rule in state:
    print(rule)
    # RuleChar({'type': 'char', 'value': [121]})   # ord("y")
    # RuleChar({'type': 'char', 'value': [110]})   # ord("n")
```

`state` is iterable. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but can easily be cast to
a list with `[*state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```python
from gbnf import GBNF

state = GBNF('root  ::= "I like green eggs and ham"')
print([*state])          # [RuleChar({'type': 'char', 'value': [73]})]   # ord("I")
state = state.add("I li")
print([*state])          # [RuleChar({'type': 'char', 'value': [107]})]  # ord("k")
state = state.add("ke gree")
print([*state])          # [RuleChar({'type': 'char', 'value': [110]})]  # ord("n")
```

`state + "..."` and `state("...")` are equivalent to `state.add("...")`.

The possible rules returned include:

- `RuleChar` - contains a list of either integers representing code points to
  match, _or_ a two-element list denoting a range within which a code point may
  appear.
- `RuleCharExclude` - contains a list of integers representing code points _not_
  to match, _or_ a two-element list denoting a range within which a code point
  may _not_ appear.
- `RuleEnd` - denotes a valid end of a string.

Invalid input raises `InputParseError`.

## Layout

The module layout mirrors the reference implementation:

| Reference (TypeScript)      | Port (Python)               |
| --------------------------- | --------------------------- |
| `src/gbnf.ts`               | `gbnf/gbnf.py`              |
| `src/grammar-graph/`        | `gbnf/grammar_graph/`       |
| `src/grammar-parser/`       | `gbnf/grammar_parser/`      |
| `src/rules-builder/`        | `gbnf/rules_builder/`       |
| `src/utils/`                | `gbnf/utils/`               |

## Tests

```sh
cd /workspace/ported_implementation
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```
