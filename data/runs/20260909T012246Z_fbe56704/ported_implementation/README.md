# GBNF (Python)

A Python port of the TypeScript `gbnf` library in `../reference_implementation`. It
parses `.gbnf` grammar files and incrementally validates input against them.

## Usage

Pass your grammar to `GBNF`:

```python
from gbnf import GBNF

state = GBNF('root ::= "yes" | "no"')
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which can be iterated over to see
which rules could come next (`state.rules()` returns the same iterator):

```python
for rule in state:
    print(rule)
    # RuleChar([121])  -> "y"
    # RuleChar([110])  -> "n"
```

States are *immutable*. To parse more input, call `state.add()` — `state + "..."` and
`state("...")` are equivalent:

```python
state = GBNF('root ::= "I like green eggs and ham"')
print([*state])       # [RuleChar([73])]
state = state.add("I li")
print([*state])       # [RuleChar([107])]
state = state + "ke gree"
print([*state])       # [RuleChar([110])]
```

Input that the grammar does not allow raises `InputParseError`. An initial string can be
passed straight to `GBNF`: `GBNF(grammar, "I li")`.

Rules are one of `RuleChar`, `RuleCharExclude` (each with a `value` list of code points
and inclusive `(start, end)` ranges) or `RuleEnd` (the input may stop here).

## Layout

The module layout mirrors the reference implementation, with names converted to
`snake_case`:

| TypeScript                       | Python                             |
| -------------------------------- | ---------------------------------- |
| `src/gbnf.ts`                    | `gbnf/gbnf.py`                     |
| `src/rules-builder/`             | `gbnf/rules_builder/`              |
| `src/grammar-parser/`            | `gbnf/grammar_parser/`             |
| `src/grammar-graph/`             | `gbnf/grammar_graph/`              |
| `src/utils/`                     | `gbnf/utils/`                      |

Two JavaScript-isms are handled explicitly rather than reproduced: indexing a string out
of bounds returns `""` (`rules_builder/char_at.py`) instead of `undefined`, and a rule id
that is never defined leaves a `None` hole in `RulesBuilder.rules` where JavaScript leaves
a sparse-array hole.

## Deviations from the reference implementation

The port is behaviour-for-behaviour identical to the reference on every valid grammar and
input that was tested (the full test suite, plus a differential harness that walked both
implementations character by character over the bundled grammars and fuzzed mutations of
them). It differs only where the reference implementation crashes with an unrelated error
or silently mis-parses:

1. **Grammar with no `root` symbol.** The reference throws
   `Error: SymbolIds does not contain key: root`, because its lookup throws before the
   `Grammar does not contain a root symbol` check can run. The port raises that intended
   `GrammarParseError`, and lists the symbols that were found (the reference's message
   serializes a map iterator, which always renders as `{}`).
2. **Undefined rule identifier referenced from a generated sub-rule.** For a grammar such
   as `root ::= jp-char+ ...` where `jp-char` is never defined, the reference throws
   `TypeError: rule is not iterable` when its validation loop reaches the sparse-array
   hole. The port raises the intended `GrammarParseError: Undefined rule identifier`.
3. **Malformed hex escape** (`\x`, `\u` or `\U` not followed by hex digits). The
   reference's `parseInt` returns `NaN`, which becomes a code point that can never match;
   the port raises a `GrammarParseError`. Well-formed escapes, and partial ones that
   `parseInt` can still read (`\x7Fz`), parse identically.
4. Internal invariant violations raise Python's `ValueError` where the reference throws a
   generic `Error`; the messages are unchanged.

## Tests

The Python test suite lives in `../tests/python`. From this directory:

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest ../tests/python
```

`python -m pytest` puts the working directory on `sys.path`, so `import gbnf` resolves
from this package root.
