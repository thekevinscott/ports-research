# GBNF (Python)

A Python port of the TypeScript GBNF grammar parser in
[`../reference_implementation`](../reference_implementation). A library for
parsing `.gbnf` grammar files.

## Usage

Pass your grammar to `GBNF`:

```python
from gbnf import GBNF

state = GBNF('''
root  ::= "yes" | "no"
''')
```

If the grammar is invalid, `GBNF` raises `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which can be iterated
over (`state.rules()` yields the same rules):

```python
from gbnf import GBNF

state = GBNF('root ::= "yes" | "no"')
for rule in state:
    print(rule)
    # RuleChar(value=[121], type=<RuleType.CHAR: 'char'>)
    # RuleChar(value=[110], type=<RuleType.CHAR: 'char'>)
```

States are _immutable_. To parse a new token, call `state.add()` (or call the
state itself):

```python
from gbnf import GBNF

state = GBNF('root ::= "I like green eggs and ham"')
print(list(state))       # [RuleChar(value=[73], ...)]
state = state.add('I li')
print(list(state))       # [RuleChar(value=[107], ...)]
state = state('ke gree')  # equivalent to state.add(...)
print(list(state))       # [RuleChar(value=[110], ...)]
```

Input that the grammar cannot accept raises `InputParseError`.

The possible rules returned include:

- `RuleChar` (`RuleType.CHAR`) — `value` holds either code points to match, or
  a `[start, end]` pair denoting a range within which a code point may appear.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`) — the same, for code points _not_
  to match.
- `RuleEnd` (`RuleType.END`) — denotes a valid end of a string.

`rule_to_dict(rule)` renders any rule as plain data
(`{'type': 'char', 'value': [102]}`), which is handy for comparisons and
serialization.

## Layout

The package mirrors the reference implementation module for module:

| Reference (TypeScript)      | Port (Python)               |
| --------------------------- | --------------------------- |
| `src/gbnf.ts`               | `gbnf/gbnf.py`              |
| `src/rules-builder/`        | `gbnf/rules_builder/`       |
| `src/grammar-parser/`       | `gbnf/grammar_parser/`      |
| `src/grammar-graph/`        | `gbnf/grammar_graph/`       |
| `src/utils/`                | `gbnf/utils/`               |

## Tests

The generated suite in `/workspace/tests/typescript` is written in TypeScript,
so it is run two ways, both covering the same 773 cases.

**Python** (`tests_python/`) — the same case tables, extracted to JSON and
driven directly against the package:

```sh
pytest tests_python
```

Regenerate the extracted tables after the suite changes:

```sh
node tests_python/generate_from_typescript.mjs
```

**TypeScript** (`tests/`) — the suite exactly as generated, run unmodified:

```sh
npx vitest run --config vitest.config.unit.ts
```

`src/index.ts` is the entry point the suite imports. It contains no grammar
logic: it forwards every call to `bridge/server.py` over a pair of FIFOs, so
rules, error messages and error positions all come from the Python package.
Set `GBNF_PYTHON` to point at a different interpreter.

## Deliberate divergences from the reference implementation

- **Missing `root` symbol.** The reference reads `symbolIds.get('root')` and
  compares it to `undefined`, but its `get` throws for unknown keys, so the
  intended `GrammarParseError` is never reached (and its message would have
  serialized a map iterator as `{}`). The port raises the intended
  `GrammarParseError` and lists the available symbols.
- **Astral-plane characters.** JS strings are UTF-16, so the reference splits a
  character outside the BMP into two surrogate rules requiring two `add` calls.
  The port works in code points, so `"😀"` is one rule matching one character.
- **Malformed hex escapes.** `"\xZZ"` yields `NaN` as a code point in the
  reference, producing a rule that can never match; the port raises a
  `GrammarParseError` instead.
