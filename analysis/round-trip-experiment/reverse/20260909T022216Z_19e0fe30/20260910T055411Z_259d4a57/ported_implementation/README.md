# GBNF (Python)

A Python port of `reference_implementation/` — a library for parsing `.gbnf`
grammar files and walking the resulting grammar graph one character at a time.

## Usage

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
list(state)  # [RuleChar(value=[102])] -- the parser will accept "f" next

next_state = state.add("f")
list(next_state)  # [RuleChar(value=[111])] -- now it will accept "o"

next_state.add("z")  # raises InputParseError
```

`GBNF(grammar, initial_string="")` returns a `ParseState`. A `ParseState` is
iterable, yielding the deduplicated set of `RuleChar` / `RuleCharExclude` /
`RuleEnd` rules that may come next. `state.add(text)` returns a *new*
`ParseState` (`state + text` is the same thing); it raises `InputParseError` if
the text is not accepted, and `GBNF` raises `GrammarParseError` for an invalid
grammar.

## Layout

The module structure mirrors the reference package one-to-one:

| reference (typescript)                | port (python)                         |
| ------------------------------------- | ------------------------------------- |
| `src/GBNF.ts`                         | `gbnf/GBNF.py`                        |
| `src/grammar-graph/*.ts`              | `gbnf/grammar_graph/*.py`             |
| `src/grammar-parser/*.ts`             | `gbnf/grammar_parser/*.py`            |
| `src/rules-builder/*.ts`              | `gbnf/rules_builder/*.py`             |
| `src/utils/**.ts`                     | `gbnf/utils/**.py`                    |

Names are snake_cased (`buildRuleStack` → `build_rule_stack`), except for the
`GBNF` entry point and the exported rule classes, which the test suite imports
by their original names.

## Tests

`tests/` is a copy of `/workspace/tests/python`, run per that suite's README:

```sh
cd /workspace/ported_implementation
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

All 773 cases pass. `/workspace/tests/typescript` is a suite for a TypeScript
port and does not apply here.

## Porting notes

- **Rule identity vs. equality.** The reference keys a `Map` on rule object
  identity in `Graph#iterateOverPointers`; `Rule.__eq__` here is by value, so
  that mapping is keyed on `id(rule)` to keep the reference's semantics. Rules
  are also hashable by value.
- **Ordering is preserved.** The reference relies on insertion-ordered `Map` and
  `Set`; python dicts are insertion-ordered, and `RuleRef.nodes` is a `list`
  rather than a `set` so that the yielded rule order stays deterministic and
  matches the reference.
- **Code points.** Python strings are sequences of code points, so `parse_char`
  consumes one position per character where the reference counts UTF-16 units.
  The two agree for everything in the BMP, which covers every grammar in the
  suite; a port that indexed UTF-16 units would be wrong for python callers.
- **Errors.** `GrammarParseError` and `InputParseError` render byte-identical
  messages to the reference and compare equal on that rendered text, which is
  what the test suite asserts. Where the reference throws a plain `Error` (a
  malformed `\xZZ` escape, a non-string input) this raises `ValueError`.
- **`type` is an instance attribute.** The reference declares `readonly type` as
  a class field, which in JS is an own property of each instance; the test suite
  sorts rules by `json.dumps(rule.__dict__)`, so `type` is set per instance here
  too rather than living only on the class.

Beyond the suite, the port was checked against the fixtures the reference
records from the original python implementation
(`reference_implementation/tests/fixtures/`): all 23,876 parse-state snapshots
in `reference-trace.json` and all 76 rendered messages in
`reference-errors.json` match, as does the `Graph.print` output pinned by
`tests/graph-print.test.ts`.
