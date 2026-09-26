# GBNF (TypeScript port)

A library for parsing `.gbnf` grammar files, ported from the Python implementation in
`../reference_implementation`.

```ts
import { GBNF } from './src/index.ts';

let state = GBNF('root ::= "foo"');
state = state.add('f');
for (const rule of state) {
  console.log(rule.type, rule.dict); // RuleChar { type: 'RuleChar', value: [111] }
}
```

## Layout

The module tree mirrors the Python package one-for-one (`snake_case` files become
`kebab-case`, `snake_case` identifiers become `camelCase`):

| Python                                  | TypeScript                                  |
| --------------------------------------- | ------------------------------------------- |
| `gbnf/__init__.py`                      | `src/index.ts`                              |
| `gbnf/GBNF.py`                          | `src/GBNF.ts`                               |
| `gbnf/grammar_graph/*.py`               | `src/grammar-graph/*.ts`                    |
| `gbnf/grammar_parser/build_rule_stack.py` | `src/grammar-parser/build-rule-stack.ts`  |
| `gbnf/rules_builder/*.py`               | `src/rules-builder/*.ts`                    |
| `gbnf/utils/**.py`                      | `src/utils/**.ts`                           |

## Running the tests

```sh
vitest run          # or: npm test
```

Vitest is installed globally in this image; there is no `node_modules` and nothing to install.
Vitest transpiles the TypeScript with esbuild, so the sources are executed as written.

Node can also run the sources directly — `node script.ts` works for any file that imports
`src/index.ts`, thanks to Node's built-in type stripping (which is why every relative import
carries an explicit `.ts` extension).

### Test suites

- `tests/iteration/`, `tests/validation/` — a port of the generated suite in
  `/workspace/tests/python`. 773 cases, the same count and the same case data as the Python
  suite, which passes identically against the reference implementation.
- `tests/unit/` — a port of the reference implementation's co-located `*_test.py` unit tests
  (188 of the reference's 190; see *Deviations* for the 2 that don't apply).

The case tables of both suites are pure data, so instead of transcribing thousands of rows by
hand they are lifted out of the Python sources into `tests/fixtures/*.json` by the scripts in
`tests/tools/`. Re-run them if the Python sources change:

```sh
python3 tests/tools/extract-python-fixtures.py
python3 tests/tools/extract-rules-builder-cases.py
```

`/workspace/tests/python/README.md` describes copying that suite into the port and running it
with pytest. That path only applies to a Python port — pytest cannot exercise a TypeScript
package — so the suite was ported instead, preserving every case verbatim.

## Deviations from the reference implementation

Behaviour is otherwise identical; these are the deliberate differences.

1. **Missing `root` symbol.** `GBNF.py` checks `symbol_ids["root"] is None`, but
   `SymbolIds.__getitem__` raises `KeyError` for an absent key, so its
   `"Grammar does not contain a 'root' symbol"` error is unreachable — a grammar with rules but
   no `root` crashes with a `KeyError`. The port checks for the key and raises the intended
   `GrammarParseError`.
2. **Python-only ergonomics.** `ParseState.__call__` and `__add__` have no TypeScript
   equivalent: `state("f")` and `state + "f"` are both `state.add("f")`. The two reference unit
   tests covering those dunder methods are therefore not ported. Iteration works through the
   normal iterator protocol (`for...of`, spread).
3. **Equality.** Python's `__eq__` overrides become explicit `equals()` methods
   (`GrammarParseError`, `InputParseError`, `Rule` and subclasses, `RuleRef`). Both error
   classes also override `toString()` to return the rendered message, so `String(err)` matches
   Python's `str(err)`; `err.message` matches `err.args[0]`.
4. **`__dict__` becomes `dict`.** `rule.dict` returns `{ type, value? }`, the same shape the
   reference serializes for rule de-duplication.
5. **Code points.** Input strings are iterated by code point (`Array.from`) and error columns
   are measured in code points, matching Python's `str` semantics. Positions *within a grammar*
   are UTF-16 indices; these agree for all Basic Multilingual Plane text (including the CJK
   grammars under test) and differ only for grammars containing astral characters.
6. **Graph internals.** The reference's `__get_root_node__`-style methods on `Graph` are
   `private` here rather than `#private`, keeping them reachable at runtime the way the Python
   tests reach them.
7. **`validateNonEmpty`** is carried over for parity but, exactly as in the reference (where it
   only appears in dataclass field metadata), is not wired into any validation path.

## Type checking

`typescript` is not installable in this offline image, so `tsc --noEmit` has not been run
against the port; vitest/esbuild strip types without checking them. `tsconfig.json` is set up
for a strict check (`allowImportingTsExtensions` + `noEmit`) once the compiler is available.
