# GBNF (Python port)

A library for parsing `.gbnf` grammar files, ported from the TypeScript implementation in
`../reference_implementation`.

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add("f")
for rule in state:
    print(rule.type, rule.__dict__)  # RuleChar {'type': 'RuleChar', 'value': [111]}
```

`state + "f"` and `state("f")` are both `state.add("f")`.

## Layout

The module tree mirrors the TypeScript one file-for-file (`kebab-case` files become
`snake_case`, `camelCase` identifiers become `snake_case`):

| TypeScript                                 | Python                                    |
| ------------------------------------------ | ----------------------------------------- |
| `src/index.ts`                             | `gbnf/__init__.py`                        |
| `src/GBNF.ts`                              | `gbnf/GBNF.py`                            |
| `src/grammar-graph/*.ts`                   | `gbnf/grammar_graph/*.py`                 |
| `src/grammar-parser/build-rule-stack.ts`   | `gbnf/grammar_parser/build_rule_stack.py` |
| `src/rules-builder/*.ts`                   | `gbnf/rules_builder/*.py`                 |
| `src/utils/**.ts`                          | `gbnf/utils/**.py`                        |

## Running the tests

There are two suites, 963 cases in total, and no third-party dependencies beyond pytest:

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest gbnf tests
```

- `tests/` — the generated suite from `/workspace/tests/python`, copied in as its README
  directs. 773 cases. It needs `pytest-describe` for its `describe_*` blocks.
- `gbnf/**/*_test.py` — the co-located unit tests, ported from the reference's
  `tests/unit/`. 190 cases, including the two `ParseState` dunder tests the reference could
  not express in TypeScript. Plain pytest; run them alone with `python -m pytest gbnf`.

`python -m pytest` (rather than a bare `pytest`) is what puts the working directory on
`sys.path`, so `import gbnf` resolves from the port root.

The rules-builder case table is ~1400 lines of rule-def literals, so it lives beside its test
as `gbnf/rules_builder/rules_builder_cases.json` — the same data the reference's
`tests/fixtures/rules-builder.json` holds.

## Differences from the reference implementation

Behaviour is otherwise identical; these are the places where the port speaks Python instead.

1. **Equality.** The reference's explicit `equals()` methods become `__eq__`
   (`GrammarParseError`, `InputParseError`, `Rule` and subclasses, `RuleRef`). `str(err)`
   renders the message, and `err.args[0]` is the message the exception was constructed with.
2. **`dict` becomes `__dict__`.** `rule.type` and `rule.value` are instance attributes, so
   `rule.__dict__` is `{'type': ..., 'value': ...}` — the shape the reference serializes for
   rule de-duplication, and what the generated suite sorts rules by.
3. **Ergonomics.** `ParseState.__add__`, `__call__`, `__len__` and `__iter__` replace the
   reference's `add`/`size`/`Symbol.iterator`. `Pointers` and `SymbolIds` likewise expose
   `__len__`/`__iter__`/`__contains__` alongside the `size`/`has` names they were ported from.
4. **JS `Map`/`Set` become `dict`/`list`.** Both preserve insertion order, which the graph
   relies on. `RuleRef.nodes` is an order-preserving, de-duplicated `list` rather than a `Set`,
   so reading it back gives an equal list, not the identical object that was assigned.
5. **Internal rule defs are dataclasses**, which is where their structural equality (used by
   `rules_builder_test.py` and `build_rule_stack_test.py`) comes from; the reference relies on
   vitest's structural comparison instead.
6. **Positions are code point offsets.** Python `str` indexes code points, so grammar
   positions and error columns are measured in code points throughout. The reference measures
   positions *within a grammar* in UTF-16 code units; the two agree for all Basic Multilingual
   Plane text (including the CJK grammars under test) and differ only for grammars containing
   astral characters.
7. **`private` methods are public.** `Graph.get_root_node`, `iterate_over_pointers` and
   friends carry no underscore, matching how the reference's tests reach them.
8. **`validate_non_empty`** is carried over for parity but, exactly as in the reference, is not
   wired into any validation path.
9. **Errors raised are `ValueError`** where the reference throws a bare `Error`;
   `GrammarParseError` and `InputParseError` are raised in exactly the same places.
