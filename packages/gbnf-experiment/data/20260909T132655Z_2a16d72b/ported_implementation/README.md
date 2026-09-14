# GBNF

A library for parsing `.gbnf` grammar files in Python. This is a port of the TypeScript
implementation in `../reference_implementation`.

## Usage

Pass your grammar to `GBNF`:

```python
from gbnf import GBNF

state = GBNF('''
root  ::= "yes" | "no"
''')
```

If the grammar is invalid, `GBNF` raises a `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```python
for rule in state:
    print(rule)
    # RuleChar([ord('y')])
    # RuleChar([ord('n')])
```

`state` is iterable. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but is easily cast to a list with
`[*state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```python
from gbnf import GBNF

state = GBNF('''
root  ::= "I like green eggs and ham"
''')
print([*state])       # [RuleChar([ord('I')])]
state = state.add("I li")
print([*state])       # [RuleChar([ord('k')])]
state = state + "ke gree"   # `+` and calling the state are aliases for `add`
print([*state])       # [RuleChar([ord('n')])]
```

If the input does not match the grammar, `add` raises an `InputParseError`.

The possible rules returned include:

- `RuleChar` — holds a list of either numbers representing code points to match, _or_ a
  two-number list denoting a range within which a code point may appear.
- `RuleCharExclude` — holds a list of numbers representing code points _not_ to match,
  _or_ a two-number list denoting a range within which a code point may _not_ appear.
- `RuleEnd` — denotes a valid end of a string.

## Tests

```sh
cd /workspace/ported_implementation
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```
