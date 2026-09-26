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
for rule in state:
    print(rule)
    # RuleChar([121])  -> ord('y')
    # RuleChar([110])  -> ord('n')
```

`state` can be iterated over. (You can also call the iterator method directly with
`state.rules()`.) `state` cannot be indexed directly, but can easily be cast to a list
with `[*state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()` (or use `+`):

```python
from gbnf import GBNF

state = GBNF('root ::= "I like green eggs and ham"')
print([*state])         # [RuleChar([73])]  -> ord('I')
state = state.add("I li")
print([*state])         # [RuleChar([107])] -> ord('k')
state = state + "ke gree"
print([*state])         # [RuleChar([110])] -> ord('n')
```

If the input does not match the grammar, `add` raises an `InputParseError`.

The possible rules returned include:

- `RuleChar` — `value` is a list of either code points to match, _or_ two-element lists
  denoting an inclusive range within which a code point may appear.
- `RuleCharExclude` — `value` is a list of code points _not_ to match, _or_ two-element
  lists denoting a range within which a code point may _not_ appear.
- `RuleEnd` — denotes a valid end of a string.

## Differences from the TypeScript implementation

- Methods and functions use `snake_case`; classes keep their original names.
- `RuleChar`, `RuleCharExclude`, and `RuleEnd` are concrete classes with value equality,
  rather than TypeScript interfaces over plain objects.
- `state + "input"` is available alongside `state.add("input")`; calling the state
  directly (`state("input")`) also works, matching the reference's callable `ParseState`.
- `InputParseError.errorForMostRecentInput` is `error_for_most_recent_input`.

## Tests

```sh
cp -r ../tests/python tests
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest tests
```
