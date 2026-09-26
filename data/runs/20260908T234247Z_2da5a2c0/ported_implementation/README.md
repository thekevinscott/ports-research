# GBNF — Python port

A Python port of the TypeScript reference implementation in `../reference_implementation`:
a library for parsing `.gbnf` grammar files and incrementally validating input against
them.

## Usage

Pass your grammar to `GBNF`:

```python
from gbnf import GBNF

state = GBNF('''
root  ::= "yes" | "no"
''')
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which is iterable:

```python
for rule in state:
    print(rule)
    # RuleChar([121])   -> ord("y")
    # RuleChar([110])   -> ord("n")
```

`state` cannot be indexed directly, but can be cast to a list with `list(state)` and
indexed that way.

States are *immutable*. To parse a new token, call `state.add()`:

```python
state = GBNF('root ::= "I like green eggs and ham"')
print(list(state))         # [RuleChar([73])]  -> ord("I")
state = state.add("I li")
print(list(state))         # [RuleChar([107])] -> ord("k")
state = state.add("ke gree")
print(list(state))         # [RuleChar([110])] -> ord("n")
```

The state is also callable, mirroring the reference's `Proxy`-based call signature:
`state("I li")` is the same as `state.add("I li")`.

The possible rules returned are:

- `RuleChar` (`RuleType.CHAR`) — `value` holds code points to match, or two-element
  `[start, end]` lists denoting an inclusive range.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`) — code points or ranges *not* to match.
- `RuleEnd` (`RuleType.END`) — denotes a valid end of a string.

Rules expose `.type`, `.value` (except `RuleEnd`) and `.to_dict()`. For convenience they
also compare equal to their plain-dict form and support `rule["type"]`, so assertions
written against the reference's plain objects work unchanged:

```python
assert list(GBNF('root ::= "a"')) == [{"type": "char", "value": [97]}]
```

Input can be a string, a single code point, or a list of code points
(`ValidInput = str | int | list[int]`), matching the reference. Input that the grammar
cannot accept raises `InputParseError`.

## Importing

The library is the `gbnf` package in this directory. All of these work:

```python
from gbnf import GBNF                     # with this directory on sys.path
from ported_implementation import GBNF    # with the repo root on sys.path
from ported_implementation.gbnf import GBNF
```

## Layout

The port mirrors the reference file-for-file, with names converted to `snake_case`:

| reference (TypeScript)                | port (Python)                            |
| ------------------------------------- | ---------------------------------------- |
| `src/gbnf.ts`                         | `gbnf/gbnf.py`                           |
| `src/index.ts`                        | `gbnf/__init__.py`                       |
| `src/grammar-graph/*.ts`              | `gbnf/grammar_graph/*.py`                |
| `src/grammar-parser/build-rule-stack.ts` | `gbnf/grammar_parser/build_rule_stack.py` |
| `src/rules-builder/*.ts`              | `gbnf/rules_builder/*.py`                |
| `src/utils/**/*.ts`                   | `gbnf/utils/**/*.py`                     |

`src/umd.ts` has no Python equivalent (it exists only to shape the UMD bundle).
`src/gbnf.ts` imports a `GBNFRule` type from `./builder/gbnf-rule.js`, but no `builder`
directory exists in the reference tree; `GBNF()` accepts a `str` or anything `str()` can
render, which is what that annotation described.

## Tests

```bash
python3 run_tests.py            # 90 tests, standard library only
python3 run_tests.py -v
```

The suite has three parts:

- `tests/test_gbnf.py` — the public API, including the reference README's examples.
- `tests/test_internals.py` — the individual ported modules.
- `tests/test_differential.py` — **the port's answers compared against the reference
  implementation's**, over a 75-case corpus (`tests/corpus.json`) and 510 seeded
  pseudo-random cases (`tests/fuzz_cases.py`). Each case compares the emitted rules,
  the state size, the rendered graph (plain and ANSI-colored) and the exact error type
  and message, for every input.

The reference's answers are checked in under `tests/golden/`, so the differential tests
run anywhere. Where Node ≥ 22.6 is available they *also* re-run the reference live and
compare against that, which is how the goldens were produced:

```bash
python3 tests/differential/generate_golden.py
```

`tests/differential/setup_reference.py` copies the reference into a scratch directory
and adjusts it so Node's `--experimental-transform-types` can execute it (rewriting
`./foo.js` specifiers to `./foo.ts` and marking type-only imports). The reference tree is
never modified.

At the time of writing, the port matches the reference on all 585 cases except the single
documented deviation below.

## Deviations from the reference

1. **A grammar with no `root` symbol raises `GrammarParseError`.** The reference intends
   this (`gbnf.ts` builds a "Grammar does not contain a root symbol" error) but the
   branch is unreachable: `symbolIds.get('root')` throws first, so the reference surfaces
   the internal `Error: SymbolIds does not contain key: root`. The port raises the
   intended `GrammarParseError`. This is the only intentional behavioural difference, and
   `tests/test_differential.py` pins it explicitly rather than ignoring it.

2. **Strings are handled as code points, not UTF-16 code units.** The reference indexes
   grammars and input by UTF-16 code unit (`charCodeAt`, `split('')`); Python strings are
   sequences of code points. The two agree for the entire Basic Multilingual Plane. They
   differ for astral characters (e.g. emoji), where the port treats one character as one
   code point — this also makes `\U0001F600`-style escapes usable, which cannot match
   anything in the reference.

3. **Malformed hex escapes raise instead of producing `NaN`.** `parseInt("ZZ", 16)` is
   `NaN` in JS, which silently yields a rule that can never match; `parse_char` raises a
   `GrammarParseError` naming the bad escape.

Everything else — rule output and ordering, graph construction, the accept/reject
decision for every input, error messages and their caret positions, and the debug graph
rendering — is reproduced exactly.

### Notes on the translation

- JS `Map`/`Set` become `dict`-backed structures, preserving insertion order, so rule
  ordering matches the reference exactly. `RuleRef.nodes` is an ordered de-duplicated
  list for the same reason.
- `GraphNode`, `GraphPointer` and `RuleRef` are identity-compared, like their JS
  counterparts. `RuleChar`/`RuleCharExclude`/`RuleEnd` are value-compared, which matches
  how the reference keys them (by serialized form).
- `RulesBuilder.rules` is a JS *sparse* array indexed by rule id; the port uses a list
  padded with `None`, so `len(rules)` matches the JS `.length` and holes are skipped
  during validation just as JS iteration skips them.
- `ParseState.__call__` replaces the `extends Function` + `Proxy` trick; the
  `[customInspectSymbol]` methods become `__repr__`.
- `GenericSet` requires hashable elements (Python), where a JS `Set` accepts anything.
  Everything the library stores in one is hashable.
