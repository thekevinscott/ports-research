# GBNF

A library for parsing `.gbnf` grammar files in Python. This is a port of the TypeScript
implementation in `reference_implementation/`.

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
from gbnf import GBNF

state = GBNF('''
root  ::= "yes" | "no"
''')
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

state = GBNF('root  ::= "I like green eggs and ham"')
print([*state])       # [RuleChar([ord("I")])]
state = state.add("I li")
print([*state])       # [RuleChar([ord("k")])]
state = state.add("ke gree")
print([*state])       # [RuleChar([ord("n")])]
```

`state + "..."` and `state("...")` are equivalent to `state.add("...")`. If the input
cannot be parsed, an `InputParseError` is raised.

The possible rules returned include:

- `RuleChar` - contains a list of either numbers representing code points to match, _or_ a
  two element list denoting a range within which a code point may appear.
- `RuleCharExclude` - contains a list of numbers representing code points _not_ to match,
  _or_ a two element list denoting a range within which a code point may _not_ appear.
- `RuleEnd` - denotes a valid end of a string.

## Differences from the TypeScript implementation

- Names are snake_case (`error_for_most_recent_input`, `is_range`, `build_rule_stack`),
  except for the `GBNF` entry point and the class names, which are kept as-is.
- Rules are classes rather than plain objects, and compare by value, so
  `RuleChar([102]) == RuleChar([102])`.
- `GrammarParseError` and `InputParseError` also compare by value, so an error raised by
  the parser equals an equivalent error constructed by hand.
- `InputParseError` normalizes its inputs to strings, so an error built from code points
  equals the same error built from the equivalent string.

## Tests

```sh
cd ported_implementation
cp -r ../tests/python tests
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```
