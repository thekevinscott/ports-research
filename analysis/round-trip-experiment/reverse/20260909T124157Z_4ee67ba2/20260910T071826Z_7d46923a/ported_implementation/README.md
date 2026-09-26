# GBNF (Python)

A Python port of `reference_implementation/` (the TypeScript `gbnf` package): a library
for parsing `.gbnf` grammar files and walking the resulting graph one code point at a
time.

## Usage

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add("f")
for rule in state:
    print(rule.type, getattr(rule, "value", None))
```

`GBNF(grammar, initial_string="")` returns a `ParseState`. Iterating a `ParseState`
yields the unique rules (`RuleChar`, `RuleCharExclude`, `RuleEnd`) that may match next.
`state.add(text)` returns a new `ParseState`, or raises `InputParseError`; `state + text`
and `state(text)` are aliases for it. Invalid grammars raise `GrammarParseError`.

## Running

The port is pure standard-library Python with no build step. Put the package root on
`sys.path` and import `gbnf`:

```sh
PYTHONPATH=/workspace/ported_implementation python3 -c 'import gbnf'
```

## Layout

`gbnf/` mirrors the reference package module for module, snake_cased:

| reference                                     | port                                        |
| --------------------------------------------- | ------------------------------------------- |
| `src/gbnf.ts`                                 | `gbnf/gbnf.py`                              |
| `src/rules-builder/rules-builder.ts`          | `gbnf/rules_builder/rules_builder.py`       |
| `src/grammar-parser/build-rule-stack.ts`      | `gbnf/grammar_parser/build_rule_stack.py`   |
| `src/grammar-graph/*.ts`                      | `gbnf/grammar_graph/*.py`                   |
| `src/utils/**.ts`                             | `gbnf/utils/**.py`                          |

JavaScript private fields (`#roots`, `#pointers`, `#valid`) become Python
name-mangled attributes (`__roots`, `__pointers`, `__valid`). TypeScript's structural
type guards (`isRuleChar`, `isRuleDefAlt`, …) become `isinstance` checks over the same
class hierarchy, so the branch selection is identical.

## Tests

The generated suite at `/workspace/tests/python` passes in full (773 cases):

```sh
cd /workspace/ported_implementation
PYTHONPATH=/workspace/ported_implementation uv run --offline --no-project \
  --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest /workspace/tests/python
```

The port was additionally cross-checked against the reference's own recorded fixtures
(`reference_implementation/tests/fixtures/`): all 41 `rules_builder` cases (symbol id
tables *and* emitted internal rules, including generated `*`/`+`/`?` sub-rules) and all
20 `build_rule_stack` (input, output) pairs match exactly.

`/workspace/tests/typescript` is the same 773 cases written against a TypeScript port
(its vitest config aliases `gbnf` to `ported_implementation/src/index.ts`); it does not
apply to a Python port.

## Notes on the port

1. **`ParseState` operators.** TypeScript has no operator overloading, so the reference
   exposes only `add(text)` and `Symbol.iterator`. Python restores the operator forms:
   `state + text` and `state(text)` both delegate to `add`, and `__len__` reports the
   number of distinct next rules.

2. **Equality.** The reference relies on structural comparison plus an `equals()` method
   on the two error classes. The port gives rules and errors a value-based `__eq__`
   (`RuleChar` never equals `RuleCharExclude`, since equality requires the same class);
   the error classes compare rendered messages, exactly as `equals()` does.

3. **`Rule.__dict__`.** `__dict__` is a property returning `{"type": ..., "value": ...}`,
   which is what the graph uses for dedupe keys and what the test suite sorts on. Real
   instance attributes are unaffected — attribute lookup goes through the instance dict
   slot, not the property.

4. **Insertion order.** The reference leans on `Map`/`Set` preserving insertion order,
   and the rule order a `ParseState` yields is asserted by the tests. Python `set` is
   unordered, so every ordered collection is a `dict`: `Pointers`, `Graph.__roots`, and
   `RuleRef.nodes` (an identity-keyed, insertion-ordered node set).

5. **Rule identity.** `Graph.iterate_over_pointers` groups pointers by rule *object*, a
   `Map` keyed by reference in the reference implementation. The port keys on `id(rule)`
   rather than the rule itself, because rules define a value-based `__eq__` and so must
   not be used as dict keys directly.

6. **Out-of-range indexing.** JavaScript's `src[pos]` yields `undefined` past the end of
   a string; Python raises `IndexError`, and a negative index wraps. The scanners use a
   `_char_at(src, pos)` helper returning `None` out of range, which preserves the
   reference's control flow (an unterminated `"` string still falls through to
   `parse_char`'s "Unexpected end of grammar input" error).

7. **Hex escapes.** `parse_char` uses `int(value, 16)` directly; the reference emulates
   it with a regex, and its comment says so.

8. **Code points.** Python indexes strings by code point, so the reference's UTF-16
   caveat does not apply: grammar positions and input conversion are code-point correct
   throughout, including astral characters.

9. **Error position rendering.** `build_error_position` can walk one line past the end of
   the input; the reference then renders a JavaScript `undefined` into the message. The
   port emits nothing for that out-of-range line instead.

10. **The parse time limit** uses `time.perf_counter()` in place of
    `performance.now() / 1000`; the units and the (effectively unreachable)
    1000-second default are unchanged.
