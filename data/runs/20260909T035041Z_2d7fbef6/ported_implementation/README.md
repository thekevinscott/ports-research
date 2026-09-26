# gbnf (Python)

A Python port of the [`gbnf`](../reference_implementation) TypeScript library: a parser for
GBNF grammar files.

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
    # {"type":"char","value":[121]}   # "y"
    # {"type":"char","value":[110]}   # "n"
```

`state` can be iterated over (you can also call the iterator method directly with
`state.rules()`). `state` cannot be indexed directly, but can easily be cast to a list with
`[*state]` and indexed that way.

States are _immutable_. To parse a new token, call `state.add()`:

```python
state = GBNF('root ::= "I like green eggs and ham"')
print([*state])        # [{"type":"char","value":[73]}]
state = state.add("I li")
print([*state])        # [{"type":"char","value":[107]}]
state = state.add("ke gree")
print([*state])        # [{"type":"char","value":[110]}]
```

A state is also callable, so `state("I li")` is equivalent to `state.add("I li")`.

The possible rules returned include:

- `RuleChar` (`RuleType.CHAR`) — `value` holds either code points to match, _or_ a
  two-element list denoting a range within which a code point may appear.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`) — `value` holds code points _not_ to match,
  _or_ a two-element list denoting a range within which a code point may _not_ appear.
- `RuleEnd` (`RuleType.END`) — denotes a valid end of a string.

Use `is_range` to tell the two forms of `value` apart:

```python
from gbnf import is_range

(rule,) = GBNF("root ::= [a-z]")
is_range(rule.value[0])  # True
```

Input may be a string, a single code point, or a list of code points. An input that the
grammar cannot match raises `InputParseError`.

## Layout

The module layout mirrors the reference implementation:

| Python                     | TypeScript                |
| -------------------------- | ------------------------- |
| `gbnf/gbnf.py`             | `src/gbnf.ts`             |
| `gbnf/rules_builder/`      | `src/rules-builder/`      |
| `gbnf/grammar_parser/`     | `src/grammar-parser/`     |
| `gbnf/grammar_graph/`      | `src/grammar-graph/`      |
| `gbnf/utils/`              | `src/utils/`              |

`gbnf/utils/js.py` is the one addition: it reproduces the JavaScript string and `parseInt`
semantics the reference implementation depends on (UTF-16 code units, out-of-range indexing
yielding `undefined`, `parseInt` parsing the longest valid prefix), so that grammars and
inputs containing astral-plane characters behave identically.

## Tests

```bash
pytest tests
```

## Known deviation from the reference implementation

One behaviour is deliberately not reproduced. While parsing, the reference implementation
stores rules in a sparse JavaScript array; a rule identifier that is referenced but never
defined leaves a hole in it. Its validation pass iterates that array with `for...of`, which
yields `undefined` for holes, so if the hole sits before the rule containing the bad
reference, the reference implementation throws `TypeError: rule is not iterable` instead of
reporting the problem. The port skips holes and reports the intended
`GrammarParseError: Undefined rule identifier "..."` in every case. This only affects
grammars that the reference implementation also rejects — no grammar that it accepts is
treated differently.

Beyond that, error _classes_ differ where the reference throws a bare `Error`: the port
raises `GBNFError` (or `GrammarParseError` / `InputParseError`, which are unchanged). The
messages are identical.
