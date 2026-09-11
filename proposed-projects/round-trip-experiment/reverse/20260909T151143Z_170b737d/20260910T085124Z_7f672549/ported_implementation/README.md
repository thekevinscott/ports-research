# GBNF (Python port)

A Python port of `reference_implementation/` — a library for parsing `.gbnf`
grammar files.

```py
from gbnf import GBNF

state = GBNF('root ::= "foo"')
list(state)      # [RuleChar(value=[102])] — the characters accepted next
state = state.add("f")
list(state)      # [RuleChar(value=[111])]
```

`state + "f"` is equivalent to `state.add("f")`.

## Layout

The module tree mirrors the reference one-to-one, so each file can be diffed
against its counterpart:

| TypeScript | Python |
| --- | --- |
| `index.ts` / `src/index.ts` | `gbnf/__init__.py` |
| `src/GBNF.ts` | `gbnf/GBNF.py` |
| `src/grammar_graph/*.ts` | `gbnf/grammar_graph/*.py` |
| `src/grammar_parser/*.ts` | `gbnf/grammar_parser/*.py` |
| `src/rules_builder/*.ts` | `gbnf/rules_builder/*.py` |
| `src/utils/**/*.ts` | `gbnf/utils/**/*.py` |

Function, method and attribute names are identical to the reference
(`parse_space`, `build_rule_stack`, `previous_code_points`, `__roots__`, …).
`src/utils/python_compat.ts` has no counterpart: it existed only to reproduce
`KeyError`, `IndexError`, string subscript bounds checking and `json.dumps`
spacing, all of which are native here.

## Running the tests

```sh
cp -r /workspace/tests/python tests
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

`python -m pytest` puts the working directory on `sys.path`, so `import gbnf`
resolves from the port root.

## Notes on fidelity

Behaviour is preserved even where the reference is surprising:

* `Rule` exposes `type` only through its `__dict__` property, so `rule.type`
  raises `AttributeError` and `Graph.print()` therefore raises for any path
  containing a `RuleEnd`/`RuleCharExclude` node.
* A grammar without a `root` rule raises `KeyError('root')`, not the
  `GrammarParseError` the surrounding code appears to intend — `SymbolIds`
  subscripting raises before the `is None` check can run.
* `Graph.__iterate_over_pointers__` seeds each rule's group with its first
  pointer and then appends that pointer again, so single-pointer groups hold
  two entries.
* `Graph`'s `unique_rules` map is written and read back in the same step, so
  the intended de-duplication of identical rules is a no-op.
* Rules are grouped by rule *identity*: `Rule.__hash__` is the identity hash
  even though `__eq__` is defined.

`RuleRef.nodes` is an insertion-ordered mapping rather than a `set`, so the
rules for a given parse state come back in grammar order rather than in an
order that changes between processes.
