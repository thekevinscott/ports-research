# GBNF (Python)

A Python port of `reference_implementation/` — a library for parsing `.gbnf` grammar files.

## Usage

Pass your grammar to `GBNF`:

```python
from gbnf import GBNF

state = GBNF('root  ::= "yes" | "no"')
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```python
for rule in state:
    print(rule)
    # RuleChar([121])  -- ord('y')
    # RuleChar([110])  -- ord('n')
```

`state` is iterable (you can also call `state.rules()` directly). It cannot be indexed,
but casts to a list with `list(state)`.

States are _immutable_. To parse a new token, call `state.add()`:

```python
state = GBNF('root ::= "I like green eggs and ham"')
print([rule.to_dict() for rule in state])   # [{'type': 'char', 'value': [73]}]
state = state.add('I li')
print([rule.to_dict() for rule in state])   # [{'type': 'char', 'value': [107]}]
state = state.add('ke gree')
print([rule.to_dict() for rule in state])   # [{'type': 'char', 'value': [110]}]
```

A `ParseState` is also callable, so `state('I li')` is the same as `state.add('I li')`.

The possible rules returned are:

- `RuleChar` (`type == RuleType.CHAR`) — holds a list of code points to match, where an
  entry may itself be a two-element list denoting an inclusive range.
- `RuleCharExclude` (`type == RuleType.CHAR_EXCLUDE`) — the same, for code points _not_ to
  match.
- `RuleEnd` (`type == RuleType.END`) — denotes a valid end of a string.

Every rule exposes `.to_dict()`, which produces the same shape the TypeScript
implementation returns (`{'type': 'char', 'value': [102]}`).

If input does not match the grammar, `add` raises `InputParseError`.

## Layout

The module tree mirrors the reference tree one-for-one, with names converted to
snake_case (`src/grammar-graph/graph-pointer.ts` → `gbnf/grammar_graph/graph_pointer.py`).

## Notable differences from the reference

These are the places where a literal transcription was not possible or not correct:

- **Iteration order.** JavaScript `Map`/`Set` preserve insertion order and the algorithm
  depends on that; the port uses `dict` (also insertion-ordered) throughout, including for
  the identity-keyed sets, which are keyed by `id()` because rules define value equality.
- **`GraphPointer.resolve` / `fetch_next` are iterative.** A pointer's parent chain grows
  with every repetition of a self-referential rule, so the reference's recursion exhausts
  Python's much smaller stack after a few hundred repetitions. Both now use an explicit
  stack; yield order is unchanged.
- **Out-of-range string indexing.** `src[pos]` returns `undefined` in JS and the reference
  relies on it. Every such read goes through `rules_builder.char_at`, which returns `''`.
- **Code points vs. UTF-16.** `get_input_as_code_points` iterates Python characters, so
  astral-plane characters are one code point; the reference splits into UTF-16 units and
  yields surrogate halves. The Python behaviour is the intended one.
- **`ParseState` callability.** The reference extends `Function` and returns a `Proxy`;
  the port defines `__call__`.
- **Missing-root error message.** The reference interpolates a `Map` iterator, which
  `JSON.stringify` renders as `{}`; the port lists the available symbol names.
- **Sparse rule arrays.** `RulesBuilder.rules` is a JS sparse array; the port pads with
  `None`, which `build_rule_stack` and the undefined-rule validation treat as a hole.

## Tests

```sh
cd /workspace/ported_implementation
pytest
```

`tests/` contains:

- `validation/`, `iteration/` — a Python translation of the generated suite in
  `/workspace/tests/javascript`. That suite is TypeScript and imports `gbnf` from
  `ported_implementation/src/index.ts`, so it cannot run against a Python
  implementation. Rather than re-type its ~3,400 lines of case tables,
  `tests/fixtures/extract.mjs` reads them straight out of the TypeScript files and emits
  `tests/fixtures/cases.json`; the Python tests parametrize over that, so both suites run
  the same cases. Re-run `node tests/fixtures/extract.mjs` if the JavaScript suite changes.
- `test_rules_builder.py` — the reference's own `rules-builder.test.ts` case table,
  extracted the same way by `tests/fixtures/extract-reference.mjs`. It pins the exact
  internal rule definitions the parser emits.
- `test_internals.py` — hand-ported versions of the reference's unit tests for the
  smaller helpers, covering the edge cases the public API only reaches indirectly.
