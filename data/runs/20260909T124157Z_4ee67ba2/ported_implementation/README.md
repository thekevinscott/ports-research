# GBNF (TypeScript)

A TypeScript port of `reference_implementation/` (the Python `gbnf` package): a library
for parsing `.gbnf` grammar files and walking the resulting graph one code point at a
time.

## Usage

```ts
import { GBNF } from './src/index.ts';

let state = GBNF('root ::= "foo"');
state = state.add('f');
for (const rule of state) {
  console.log(rule.type, 'value' in rule ? rule.value : undefined);
}
```

`GBNF(grammar, initialString?)` returns a `ParseState`. Iterating a `ParseState` yields
the unique rules (`RuleChar`, `RuleCharExclude`, `RuleEnd`) that may match next.
`state.add(text)` returns a new `ParseState`, or throws `InputParseError`. Invalid
grammars throw `GrammarParseError`.

## Running

The port has no dependencies and no build step: Node ≥ 22.6 strips the types and runs
the `.ts` files directly, and the tests use the built-in `node:test` runner.

```sh
cd /workspace/ported_implementation
node --test 'tests/**/*.test.ts'   # or: npm test
```

There is no `tsc` in this image and no npm registry access, so the port is written in
erasable-syntax-only TypeScript (no `enum`, no namespaces, no constructor parameter
properties) — everything Node can strip without a transform.

## Layout

`src/` mirrors the reference package module for module, kebab-cased:

| reference                                   | port                                          |
| ------------------------------------------- | --------------------------------------------- |
| `gbnf/GBNF.py`                              | `src/gbnf.ts`                                 |
| `gbnf/rules_builder/rules_builder.py`       | `src/rules-builder/rules-builder.ts`          |
| `gbnf/grammar_parser/build_rule_stack.py`   | `src/grammar-parser/build-rule-stack.ts`      |
| `gbnf/grammar_graph/*.py`                   | `src/grammar-graph/*.ts`                      |
| `gbnf/utils/**.py`                          | `src/utils/**.ts`                             |

Python's name-mangled attributes (`__roots__`, `__pointers__`, …) become JavaScript
private fields (`#roots`, `#pointers`). Where a private member was reachable from the
reference's own tests (`graph.__get_root_node__`, `graph.__iterate_over_pointers__`),
the port exposes it as a normal method.

## Tests

`tests/` holds two suites, 961 tests in total:

- `tests/iteration/` and `tests/validation/` — a translation of `/workspace/tests/python`,
  the generated Python suite. It runs the same 773 cases: the parametrize tables are
  extracted from the Python source into `tests/fixtures/` by
  `tests/tools/extract-cases.py` rather than retyped, so the two suites provably share
  their inputs. `tests/grammars/` is a copy of the suite's grammar corpus.
- `tests/unit/` — a translation of the reference package's own unit tests (the
  `gbnf/**/*_test.py` files).

Regenerating the fixtures:

```sh
python3 tests/tools/extract-cases.py            # from /workspace/tests/python
python3 tests/tools/extract-internal-cases.py   # rules_builder_test's table
```

Two of the reference's internal test files needed special handling:

- `rules_builder_test.py` keeps its 41 cases in a module-level `test_cases` list, read
  out with `ast` + `eval` and serialized to `tests/fixtures/rules_builder_test.json`.
- `build_rule_stack_test.py` spreads its inputs across inline asserts, locals and
  parametrize tables. Instead of scraping each shape, `tests/tools/record-build-rule-stack.py`
  is a pytest plugin that runs the reference suite with `build_rule_stack` wrapped in a
  recorder, capturing the 20 unique (input, output) pairs those tests assert on. The
  reference suite passes, so the recorded outputs *are* its expectations.

Reference tests that patch a module-level function purely to force a branch
(`get_serialized_rule_key_test`, `graph_pointer_test`, `print_test`, `graph_node_test`)
are ported without mocking: the real type guards select the same branches for the same
inputs. Where a mock changed the *expected value* rather than the branch, the port
asserts the real function's output and says so in a comment — see
`tests/unit/grammar-graph/print.test.ts`.

## Intentional differences from the reference

1. **`ParseState` operators.** Python's `state(text)`, `state + text` and `iter(state)`
   all funnel into `add`/`rules`. TypeScript has no operator overloading, so `add(text)`
   is the single entry point; `ParseState` implements `Symbol.iterator`.

2. **Equality.** The reference gives rules and errors a value-based `__eq__`. The port
   relies on structural comparison (`assert.deepStrictEqual`, which is prototype-aware,
   so `RuleChar` never equals `RuleCharExclude`) and exposes `equals()` on the two error
   classes, which compare rendered messages exactly as Python's `__eq__` does.

3. **Missing `root` symbol.** `GBNF.py` checks `if symbol_ids["root"] is None`, but
   `SymbolIds.__getitem__` raises `KeyError` for an absent key, so the intended
   `GrammarParseError("Grammar does not contain a 'root' symbol")` is unreachable. The
   port raises that error. No test covers the branch in either implementation.

4. **`Graph.print()` with an end rule.** `print.py` reads `rule.type`, which raises
   `AttributeError` in Python because `Rule.__dict__` is overridden as a property and
   never consulted for attribute lookup — so printing any graph containing a `RuleEnd`
   crashes upstream. The port implements `Rule#type` (the class name, which is what
   `__dict__` reports) and prints `RuleEnd`.

5. **Serialized rule keys.** `get_serialized_rule_key` uses `JSON.stringify`, which omits
   the spaces `json.dumps` inserts after commas (`1-[97,98]` vs `1-[97, 98]`). The key is
   an internal dedupe key and never surfaces; both are injective over the same values.

6. **Code points.** Python indexes strings by code point; JavaScript by UTF-16 unit. The
   two agree for every character in the BMP, which covers the whole grammar corpus.
   Input conversion (`getInputAsCodePoints`, `getInputAsString`) is fully code-point
   correct, including astral characters. Grammar *positions* inside `RulesBuilder` and
   the error renderers are UTF-16 based, so a grammar containing an astral character
   would report a position the reference would count differently.

7. **The parse time limit** uses `performance.now() / 1000` in place of
   `time.perf_counter()`; the units and the (effectively unreachable) 1000-second default
   are unchanged.
