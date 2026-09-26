# gbnf (Python)

A Python port of the TypeScript `gbnf` package in `../reference_implementation`: a
library for parsing [GBNF](https://github.com/ggerganov/llama.cpp/blob/master/grammars/README.md)
grammars and walking the resulting graph one code point at a time.

## Usage

```python
from gbnf import GBNF, InputParseError

state = GBNF('root ::= "foo" | "bar"')
[rule.to_dict() for rule in state]
# [{'type': 'char', 'value': [102]}, {'type': 'char', 'value': [98]}]

state = state.add('f')          # or: state('f')
[rule.to_dict() for rule in state]
# [{'type': 'char', 'value': [111]}]

[rule.to_dict() for rule in state.add('oo')]
# [{'type': 'end'}]

state.add('x')                  # raises InputParseError
```

`GBNF(grammar, initial_string='')` returns a `ParseState`. Iterating a `ParseState`
yields the rules that may come next (`RuleChar`, `RuleCharExclude`, `RuleEnd`);
`add()` consumes more input and returns the next state, raising `InputParseError`
when the input can no longer satisfy the grammar. An unparseable grammar raises
`GrammarParseError`.

## Layout

The module tree mirrors the reference implementation one-for-one, with names
converted to `snake_case`:

| TypeScript                            | Python                                 |
| ------------------------------------- | -------------------------------------- |
| `src/index.ts`                        | `gbnf/__init__.py`                     |
| `src/gbnf.ts`                         | `gbnf/gbnf.py`                         |
| `src/rules-builder/*`                 | `gbnf/rules_builder/*`                 |
| `src/grammar-parser/build-rule-stack` | `gbnf/grammar_parser/build_rule_stack` |
| `src/grammar-graph/*`                 | `gbnf/grammar_graph/*`                 |
| `src/utils/*`                         | `gbnf/utils/*`                         |

`gbnf/utils/js.py` is the one addition: helpers for the JavaScript string
semantics the parsers rely on (`src[pos]` past the end of a string yields
`undefined` rather than throwing, and `parseInt` parses a leading prefix).

Where the reference relies on JavaScript's insertion-ordered `Map`/`Set`, the port
uses `dict` (iteration order is load-bearing — it determines the order in which
rules come out of a `ParseState`). Rules are compared by identity, as object
references are in the reference implementation.

## Tests

```sh
cd /workspace/ported_implementation
pytest tests -q      # 773 tests
```

`tests/` is a translation of the JavaScript suite in `/workspace/tests/javascript`:
every case table was extracted from the `.test.ts` sources programmatically and
emitted as `pytest.mark.parametrize` data, so the Python suite asserts the same
773 cases as the original. Test ids match the `(%#)` indices in the JS test names.

The JS suite could not be run directly against this port: it is a vitest suite that
imports a TypeScript entry point, and the npm registry is not reachable from this
environment (`npm view vitest` returns 403), so vitest cannot be installed.

As an additional check, the port was differentially tested against the reference
implementation itself, run under `node --experimental-transform-types`: 2733
grammar/input pairs (every grammar and input in the test suite, plus fuzzed inputs)
produced byte-identical rule sets at every step and identical error messages, as did
graph `print()` output. ~1900 randomly mutated grammars agreed except for the
divergences below.

## Known divergences from the reference

All four are in malformed-grammar handling; no case was found where the reference
succeeds and the port fails.

1. **Grammar without a `root` symbol.** The reference intends to raise
   `GrammarParseError('Grammar does not contain a root symbol...')` but its
   `SymbolIds.get` throws first, so callers see a bare
   `Error: SymbolIds does not contain key: root`. The port raises the intended
   `GrammarParseError`.
2. **Undefined rule identifier that leaves a gap in the rule list.** The reference
   iterates its sparse rules array and crashes with `TypeError: rule is not
   iterable` before its validation can report the problem. The port reports the
   intended `GrammarParseError: Undefined rule identifier "<name>"`.
3. **Invalid hex escape** (e.g. `\xZZ`). `parseInt` yields `NaN` in the reference,
   producing a rule that silently matches nothing; the port raises
   `GrammarParseError: Invalid escape`.
4. **Unbounded recursion** (e.g. a left-recursive grammar) surfaces as
   `RecursionError` rather than a stack-overflow `RangeError`.

Internal invariant violations that the reference raises as a generic `Error` are
raised as `ValueError` here, with the same message.
