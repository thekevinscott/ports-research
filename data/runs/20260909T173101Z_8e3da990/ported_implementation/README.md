# GBNF (Python port)

A Python port of `reference_implementation/` (the `gbnf` TypeScript package): a
library for parsing GBNF grammars.

## Usage

```python
from ported_implementation import GBNF

state = GBNF('root ::= "yes" | "no"')
for rule in state:
    print(rule)
    # RuleChar(type=<RuleType.CHAR: 'char'>, value=[121])
    # RuleChar(type=<RuleType.CHAR: 'char'>, value=[110])
```

States are immutable; `add` (or calling the state) returns the next state:

```python
state = GBNF('root ::= "I like green eggs and ham"')
state = state.add('I li')
[rule.value for rule in state]   # [[107]]  -> "k"
state = state('ke gree')         # same as state.add(...)
[rule.value for rule in state]   # [[110]]  -> "n"
```

The rules returned are `RuleChar`, `RuleCharExclude` and `RuleEnd`. Each has a
`type` and (except for `RuleEnd`) a `value` of code points and inclusive
`[start, end]` ranges. Rules also support mapping-style access (`rule['type']`,
`dict(rule)`) and compare equal to the equivalent dict, which keeps assertions
short.

Invalid grammars raise `GrammarParseError`; input that the grammar cannot match
raises `InputParseError`.

## Layout

The module layout mirrors `reference_implementation/src/`, with kebab-case file
names converted to snake_case:

| reference | port |
| --- | --- |
| `src/index.ts` | `__init__.py` |
| `src/gbnf.ts` | `gbnf.py` |
| `src/rules-builder/` | `rules_builder/` |
| `src/grammar-parser/` | `grammar_parser/` |
| `src/grammar-graph/` | `grammar_graph/` |
| `src/utils/` | `utils/` |

Functions and methods are snake_case, with the reference's camelCase names kept
as aliases (`parseChar`, `isRange`, `fetchNext`, …).

## Deviations from the reference

Everything else — including error messages, rule ordering and the graph's debug
`print()` output — matches the reference implementation; it was checked against
it across ~4,100 grammar/input cases (see `tests/`).

1. **Code points, not UTF-16 code units.** The reference walks strings with
   `charCodeAt`, so a character outside the Basic Multilingual Plane (an emoji,
   say) is two surrogate halves both in a grammar literal and in input. Python
   strings are sequences of code points, so such a character is one rule and one
   input step here. Behaviour is identical for the entire BMP, and this also
   makes `\U0001F600`-style escapes match the input they describe, which they do
   not in the reference.

2. **Recursion is bounded explicitly.** Graph traversal is iterative rather than
   recursive, so deeply nested input no longer depends on the interpreter's
   stack (the reference overflows at roughly 1,875 levels of right recursion;
   the port keeps going). A grammar that can recurse *without consuming input* —
   `("a"*)+`, `("a"?)*` — is still rejected, but with an explicit
   `RecursionError` rather than a stack overflow.
