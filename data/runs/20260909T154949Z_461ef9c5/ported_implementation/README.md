# gbnf (Python)

A Python port of `../reference_implementation` — a library for parsing GBNF grammars and
walking the resulting graph one character at a time.

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
[rule.as_dict() for rule in state]   # [{'type': 'char', 'value': [102]}]

state = state.add('f')
[rule.as_dict() for rule in state]   # [{'type': 'char', 'value': [111]}]

state = state.add('oo')
[rule.as_dict() for rule in state]   # [{'type': 'end'}]
```

`GBNF(grammar, initial_string='')` returns a `ParseState`. Iterating a `ParseState` yields
the rules that may match next (`RuleChar`, `RuleCharExclude`, `RuleEnd`); `state.add(input)`
returns a new `ParseState` advanced past `input`, or raises `InputParseError`. An invalid
grammar raises `GrammarParseError`.

## Layout

The module tree mirrors the TypeScript source file-for-file:

| TypeScript | Python |
| --- | --- |
| `src/index.ts` | `gbnf/__init__.py` |
| `src/gbnf.ts` | `gbnf/gbnf.py` |
| `src/rules-builder/*.ts` | `gbnf/rules_builder/*.py` |
| `src/grammar-parser/build-rule-stack.ts` | `gbnf/grammar_parser/build_rule_stack.py` |
| `src/grammar-graph/*.ts` | `gbnf/grammar_graph/*.py` |
| `src/utils/**/*.ts` | `gbnf/utils/**/*.py` |

Two names differ to avoid collisions: `grammar-graph/print.ts` is `grammar_graph/print_.py`,
and the shared `ValidInput` alias lives in `gbnf/valid_input.py` (importing it from
`grammar_graph/types.py` would make `gbnf.utils.errors` and `gbnf.grammar_graph` circular).

## Tests

```sh
cd /workspace/ported_implementation
pytest tests -q
```

`tests/` is a case-for-case port of the generated suite in `/workspace/tests/javascript`.
That suite is TypeScript (vitest, importing a `.ts` entry point), so it cannot execute
against Python; each `test.for` table was extracted mechanically and re-emitted as
`pytest.mark.parametrize` data, preserving every case and its expected value. 773 tests.

## Intentional deviations from the reference

* **Callable `ParseState`.** The TS class wraps itself in a `Proxy` so instances are
  callable. Python `__call__` provides the same thing without the indirection.
* **Rule equality.** TS keys `Map<UnresolvedRule, ...>` by object identity, relying on the
  graph having already collapsed structurally identical rules onto one instance. The Python
  rules use value equality/hashing, which is equivalent given that same de-duplication.
* **`as_dict()` on rules.** Added for ergonomics; the TS rules were plain objects, so tests
  and callers compared them directly as data.
* **Missing-root message.** TS interpolates `JSON.stringify(symbolIds.keys())`, which
  stringifies an iterator to `{}`. The port lists the actual symbol names instead.
* **Sparse rule arrays.** JS grows arrays with holes on out-of-order index assignment; the
  Python `RulesBuilder` pads with `None` and the validation pass skips those slots.
* Rules-builder helpers take an explicit bounds-checked `_at(pos)` accessor where the TS
  relied on out-of-range indexing returning `undefined`.

## Verification

Beyond the ported suite, the port was differentially tested against the reference: the
TypeScript source was executed under Node's `--experimental-transform-types` and both
implementations were run over 1188 randomized inputs across every grammar mentioned in the
test suite, comparing the rule set after each character plus all error messages. No
divergence.
