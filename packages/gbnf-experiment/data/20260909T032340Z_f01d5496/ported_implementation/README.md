# GBNF

A library for parsing `.gbnf` grammar files in Python. A port of the TypeScript
implementation in `../reference_implementation`.

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
for rule in state:
    print(rule)
    # RuleChar([ord("y")])
    # RuleChar([ord("n")])
```

`state` can be iterated over. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but can easily be cast to a list
with `[*state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```python
from gbnf import GBNF

state = GBNF('root ::= "I like green eggs and ham"')
print([*state])          # [RuleChar([ord("I")])]
state = state.add("I li")
print([*state])          # [RuleChar([ord("k")])]
state = state.add("ke gree")
print([*state])          # [RuleChar([ord("n")])]
```

`state + "ke gree"` and `state("ke gree")` are equivalent to `state.add("ke gree")`.

The possible rules returned include:

- `RuleChar` - contains a list of either numbers representing code points to match, _or_
  a two element list denoting a range within which a code point may appear.
- `RuleCharExclude` - contains a list of numbers representing code points _not_ to
  match, _or_ a two element list denoting a range within which a code point may _not_
  appear.
- `RuleEnd` - denotes a valid end of a string.

If the input does not match the grammar, `add` raises `InputParseError`.

## Layout

The module tree mirrors the reference implementation:

| Python                              | TypeScript                          |
| ----------------------------------- | ----------------------------------- |
| `gbnf/gbnf.py`                      | `src/gbnf.ts`                       |
| `gbnf/grammar_graph/`               | `src/grammar-graph/`                |
| `gbnf/grammar_parser/`              | `src/grammar-parser/`               |
| `gbnf/rules_builder/`               | `src/rules-builder/`                |
| `gbnf/utils/`                       | `src/utils/`                        |

## Tests

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest tests
```
