# GBNF (Python port)

A Python port of `../reference_implementation` — a library for parsing `.gbnf` grammars and
walking a grammar graph one input character at a time.

```py
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add("f")
for rule in state:
    print(rule.to_dict())  # {'type': 'RuleChar', 'value': [111]}
```

## Layout

The module structure mirrors the TypeScript reference one-to-one, with `camelCase` file and
identifier names converted back to Python's `snake_case`:

| TypeScript | Python |
| --- | --- |
| `src/GBNF.ts` | `gbnf/GBNF.py` |
| `src/rulesBuilder/` | `gbnf/rules_builder/` |
| `src/grammarParser/` | `gbnf/grammar_parser/` |
| `src/grammarGraph/` | `gbnf/grammar_graph/` |
| `src/utils/` | `gbnf/utils/` |

TypeScript constructs without a direct Python equivalent are mapped as follows:

- `[Symbol.iterator]()` becomes `__iter__`; the `size` getter becomes `__len__`, so a
  `ParseState` is also truthy exactly when it has rules.
- `parseState.add(text)` is joined by `parseState + text` and `parseState(text)`, which the
  TypeScript port had dropped for lack of operator overloading.
- `src/utils/repr.ts` has no counterpart: it only existed to reproduce Python's `repr()` and
  `json.dumps()` in JavaScript, so the port uses `repr()` and `json.dumps` directly.
- JavaScript's out-of-bounds string indexing (`src[pos]` → `undefined`) has no Python
  equivalent — `IndexError` would be raised instead — so the parsers read through a
  `_char_at(src, pos)` helper that returns `""` past the end. This keeps the guards that the
  reference relies on, such as raising `GrammarParseError: Expecting ')' at ...` for an
  unterminated group rather than crashing.
- `throw new Error(...)` becomes `raise ValueError(...)` with the same message. Unbounded
  grammars (e.g. `root ::= "a"**`) raise `RecursionError` where JavaScript raised
  `RangeError: Maximum call stack size exceeded`.
- Sets and maps whose iteration order the graph depends on (`RuleRef.nodes`, `Pointers`) are
  lists and dicts here, since a Python `set` of objects does not preserve insertion order
  the way a JavaScript `Set` does.

Rule classes compare by value and expose `type` as a property, so `RuleChar([102])` equals
another `RuleChar([102])` but never a `RuleCharExclude([102])`, and `rule.__dict__` stays
JSON-serializable.

## Tests

`tests/` is the generated Python suite, copied in per its README:

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest tests
```
