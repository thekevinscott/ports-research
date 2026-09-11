# GBNF (Python port)

A Python port of the TypeScript `gbnf` package in `reference_implementation/` — a
library for parsing `.gbnf` grammar files.

## Usage

Pass your grammar to `GBNF`:

```python
from ported_implementation import GBNF

state = GBNF('root ::= "yes" | "no"')
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```python
for rule in state:
    print(rule)
    # RuleChar(value=[121])   # ord('y')
    # RuleChar(value=[110])   # ord('n')
```

`state` is iterable. It cannot be indexed directly, but casts to a list with
`list(state)` or `[*state]`. `len(state)` (or `state.size`) gives the number of
distinct rules.

States are _immutable_. To parse a new token, call `state.add()`:

```python
state = GBNF('root ::= "I like green eggs and ham"')
print([*state])         # [RuleChar(value=[73])]   # ord('I')
state = state.add("I li")
print([*state])         # [RuleChar(value=[107])]  # ord('k')
state = state.add("ke gree")
print([*state])         # [RuleChar(value=[110])]  # ord('n')
```

A state is also callable, so `state("I li")` is equivalent to `state.add("I li")`.
Input may be a `str`, a single code point (`int`), or a list of code points.
Input the grammar cannot accept raises `InputParseError`.

The possible rules returned include:

- `RuleChar` (`RuleType.CHAR`, `"char"`) — `value` holds code points to match, where
  an entry may itself be a two-element `[start, end]` range.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`, `"char_exclude"`) — as above, but code
  points that must _not_ match.
- `RuleEnd` (`RuleType.END`, `"end"`) — denotes a valid end of a string.

Rules compare equal to plain dicts and support `rule["type"]` / `rule.to_dict()`,
so they are straightforward to assert against:

```python
assert [*GBNF("root ::= [a-z]")] == [{"type": "char", "value": [[97, 122]]}]
```

## Layout

The module tree mirrors the reference implementation one-for-one (kebab-case file
names become snake_case):

| reference | port |
| --- | --- |
| `src/gbnf.ts` | `gbnf.py` |
| `src/grammar-graph/*` | `grammar_graph/*` |
| `src/grammar-parser/build-rule-stack.ts` | `grammar_parser/build_rule_stack.py` |
| `src/rules-builder/*` | `rules_builder/*` |
| `src/utils/**` | `utils/**` |

Functions are exposed under snake_case names, with camelCase aliases kept where the
reference exported them (`is_range`/`isRange`, `parse_char`/`parseChar`, …).

## Tests

```bash
pytest ported_implementation/tests
```

The suite's expected values were verified against the reference implementation by
running it under Node's TypeScript support, plus a differential fuzz harness over
75,000 randomly generated grammar/input pairs.

## Intentional divergences from the reference

1. **Missing `root` symbol.** The reference reaches for `symbolIds.get('root')`
   before its own `undefined` check can fire, so a rootless grammar surfaces a bare
   `Error: SymbolIds does not contain key: root` and its
   `Grammar does not contain a root symbol` branch is unreachable. The port checks
   membership first and raises that intended `GrammarParseError`.

2. **Unicode beyond the BMP.** The reference walks JavaScript strings as UTF-16 code
   units; the port walks Python strings as code points. Results are identical for
   BMP text. For astral characters the port is consistent where the reference is not
   — `root ::= "\U0001F600"` matches `"😀"` here, whereas the reference builds a rule
   for `U+1F600` but then feeds it a lone surrogate and fails.

3. **Runtime error types.** JavaScript's bare `Error` becomes `Exception` (and
   `SymbolIds` lookups raise `SymbolIdsKeyError`, a `KeyError` subclass whose message
   matches the reference's). Blowing the stack on a left-recursive grammar raises
   `RecursionError` rather than `RangeError`.

The reference's `src/umd.ts` (CommonJS/UMD bundle wiring) has no Python equivalent
and is not ported. `src/gbnf.ts` imports a `GBNFRule` builder type from a `./builder`
module that is not present in `reference_implementation/`; the port accepts any
object and falls back to `str(input)`, matching what the reference does with
`input.toString()`.
