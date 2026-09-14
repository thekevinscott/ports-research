# GBNF (Python port)

A Python port of the JavaScript [`gbnf`](../reference_implementation) library: a
parser for `.gbnf` grammar files that tells you, at any point in a string, which
characters may come next.

## Usage

Pass your grammar to `GBNF`:

```python
from gbnf import GBNF

state = GBNF('''
root  ::= "yes" | "no"
''')
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which can be iterated over
(or iterated explicitly with `state.rules()`):

```python
for rule in state:
    print(rule)
    # RuleChar(value=[121], type=<RuleType.CHAR: 'char'>)   # "y"
    # RuleChar(value=[110], type=<RuleType.CHAR: 'char'>)   # "n"
```

`state` cannot be indexed directly, but casts to a list with `list(state)`.

States are _immutable_. To parse a new token, call `state.add()`:

```python
from gbnf import GBNF

state = GBNF('root ::= "I like green eggs and ham"')
print(list(state))       # [RuleChar(value=[73])]   # "I"
state = state.add("I li")
print(list(state))       # [RuleChar(value=[107])]  # "k"
state = state.add("ke gree")
print(list(state))       # [RuleChar(value=[110])]  # "n"
```

The rules returned are:

- `RuleChar` — `value` holds code points to match, or two element `[start, end]`
  lists denoting an inclusive range within which a code point may appear.
- `RuleCharExclude` — the same, for code points that must _not_ match.
- `RuleEnd` — denotes a valid end of a string.

Each carries a `type` of `RuleType.CHAR`, `RuleType.CHAR_EXCLUDE` or
`RuleType.END`, whose values are the strings `"char"`, `"char_exclude"` and
`"end"` — the same values the JavaScript library uses.

## API mapping

The module layout mirrors the reference tree, with names converted to
`snake_case`:

| JavaScript                     | Python                                |
| ------------------------------ | ------------------------------------- |
| `GBNF(grammar, initialString)` | `GBNF(grammar, initial_string)`        |
| `state.add(input)`             | `state.add(input)`                     |
| `state(input)`                 | `state(input)`                         |
| `[...state]`                   | `list(state)`                          |
| `state.size`                   | `state.size` / `len(state)`            |
| `state.grammar`                | `state.grammar`                        |
| `isRange(value)`               | `is_range(value)`                      |
| `err.errorForMostRecentInput`  | `err.error_for_most_recent_input`      |
| `err.src`                      | `err.src`                              |

`GrammarParseError` and `InputParseError` are exceptions; their rendered
messages (including the caret position block) match the reference byte for byte.

## Tests

The generated suite in `/workspace/tests` is written in TypeScript and imports
`gbnf` from a `.ts` entry point, so it cannot execute against a Python package.
Its case tables are instead extracted verbatim into JSON fixtures and driven by
the Python suite, so both implementations are checked against identical data:

```sh
# regenerate the fixtures after the JavaScript suite changes (requires node)
node tests/fixtures/extract.mjs

# run the suite
python3 -m unittest discover -s tests -t . -p "test_*.py"
```

That covers all 773 cases of the generated suite. `tests/unit/` additionally
ports the reference's own unit tests for the parsing and error helpers.

### Differential testing

`tools/differential/run.py` runs the same grammars and inputs through the
reference TypeScript sources (loaded directly with node's
`--experimental-transform-types`) and through this port, then compares the
traces — the rules yielded on construction, after applying a whole input, and
after applying that input one character at a time, plus the exact text of any
error raised:

```sh
python3 tools/differential/run.py --grammars 200 --mutations 4
```

Grammars are also randomly mutated to exercise the error paths. The run exits
non-zero if any difference falls outside the deviations listed below.

## Deviations from the reference

Behaviour is otherwise identical, including error message text. These four cases
differ deliberately:

1. **Missing `root` symbol.** The reference reaches
   `symbolIds.get('root')`, whose lookup throws first, so it reports the internal
   `SymbolIds does not contain key: root` and its own
   "Grammar does not contain a root symbol" branch is unreachable. The port
   raises that intended `GrammarParseError` instead, listing the available
   symbols.
2. **A rule that is referenced but never defined, when its slot precedes a rule
   that is defined.** Validation in the reference iterates a sparse array and
   hits the hole, failing with `TypeError: rule is not iterable`. The port
   reports the intended `GrammarParseError: Undefined rule identifier "<name>"`.
3. **Escapes with no hex digits** (`"\xzz"`). `parseInt` yields `NaN` in the
   reference, which silently builds a rule that can never match; the port raises
   a `GrammarParseError` pointing at the escape. Escapes with _some_ hex digits
   (`"\x4z"`) follow `parseInt`'s prefix parsing exactly, as the reference does.
4. **Characters outside the Basic Multilingual Plane.** JavaScript strings are
   UTF-16, so the reference splits an emoji into two surrogate code points and
   counts it as two characters when positioning error carets. Python strings are
   sequences of code points, so the port treats it as one. Everything in the BMP
   — which includes every case in the test suites — behaves identically.

A stack overflow on a left-recursive grammar surfaces as `RecursionError` rather
than `RangeError`; note that Python's recursion limit is reached at a shallower
nesting depth than V8's.
