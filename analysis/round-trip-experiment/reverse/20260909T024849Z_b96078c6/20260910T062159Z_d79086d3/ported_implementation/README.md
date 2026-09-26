# GBNF (Python)

A Python port of `reference_implementation/` (the TypeScript `gbnf` package): a library
for parsing `.gbnf` grammar files and walking the resulting grammar graph.

```python
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add("f")
list(state)  # => [RuleChar(value=[111])]  (the rules that may come next)
len(state)   # => 1
```

## Layout

The port mirrors the reference package one file at a time; `kebab-case` file names become
`snake_case` module names, and `camelCase` functions become `snake_case`. This is the
module layout the reference's own `gbnf/**` compatibility tree describes.

| TypeScript                                   | Python                                  |
| -------------------------------------------- | --------------------------------------- |
| `src/gbnf.ts`                                 | `gbnf/GBNF.py`                           |
| `src/index.ts`                                | `gbnf/__init__.py`                       |
| `src/utils/is-point-in-range.ts`              | `gbnf/utils/is_point_in_range.py`        |
| `src/utils/validate-non-empty.ts`             | `gbnf/utils/validate_non_empty.py`       |
| `src/utils/errors/*.ts`                       | `gbnf/utils/errors/*.py`                 |
| `src/rules-builder/*.ts`                      | `gbnf/rules_builder/*.py`                |
| `src/grammar-parser/build-rule-stack.ts`      | `gbnf/grammar_parser/build_rule_stack.py`|
| `src/grammar-graph/*.ts`                      | `gbnf/grammar_graph/*.py`                |
| `src/utils/code-points.ts`                    | — (see below)                            |

The reference's `src/compat.ts` (`snake_case` aliases) has no counterpart: the Python
names *are* the `snake_case` ones.

Methods the reference documents as spelled `__like_this__` on the Python side keep that
spelling here: `Graph.getRootNode` → `Graph.__get_root_node__`, `getInitialPointers` →
`__get_initial_pointers__`, `parse` → `__parse__`, `resolvePointer` →
`__resolve_pointer__`, `fetchNodesForRootNode` → `__fetch_nodes_for_root_node__`,
`iterateOverPointers` → `__iterate_over_pointers__`. (Names with two leading *and*
trailing underscores are not name-mangled, and are not private.)

JavaScript's `Symbol.iterator` becomes `__iter__`, and `ParseState.add(text)` is
additionally reachable as `state + text` (`__add__`) and `state(text)` (`__call__`).

## Tests

```sh
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
  python -m pytest tests
```

`python -m pytest` puts the working directory on `sys.path`, so `import gbnf` resolves
from this directory.

## Porting notes

The port is behaviour-for-behaviour with the reference. Every place the two could
diverge, and the language-level decisions that needed making:

- **Code points.** The reference walks `Array.from(src)` because JavaScript indexes
  strings by UTF-16 code unit, and every position and length in the library is a code
  point index. Python indexes strings by code point already, so `src/utils/code-points.ts`
  has no counterpart — plain `str` indexing is what the helpers were emulating.
- **Equality.** The reference notes that Python's `__eq__` overloads on `Rule`,
  `InternalRuleDef*`, `GrammarParseError` and `InputParseError` cannot be expressed in
  JavaScript, and uses structural comparison there instead. Those `__eq__` methods are
  restored here. `InputParseError.__eq__` compares the *rendered* inputs, since the same
  input can arrive either as a string or as a list of code points.
- **Hashing.** Rules are grouped by identity, not equality, while walking the graph, so
  `Rule.__hash__` stays identity based (`id(self)`) even though `__eq__` is structural.
  `Graph.__iterate_over_pointers__` keys its mapping on `id(rule)` outright, so a hash
  collision between two structurally equal rules can never merge them.
- **`Rule.type`.** A real attribute, set in `Rule.__init__`, so that `rule.__dict__` is
  `{"type": ..., "value": ...}` — the shape the reference's `Rule.toJSON()` produces, and
  what `ParseState.rules()` de-duplicates on. `Graph.print()` also depends on it, and
  works: `{0,0,0}[f]-> {0,0,1}[o]-> {0,0,2}[o]-> {0,0,3}RuleEnd`.
- **Bounds checks.** Reading past the end of an array gives `undefined` in JavaScript and
  raises `IndexError` in Python, so the parsers use a `_char_at` helper that returns
  `None` out of bounds. `root ::= "foo`, `root ::= [a-z` and `root ::= ("a"` therefore
  reach the same `GrammarParseError`s the reference raises, rather than an `IndexError`.
- **`RuleRef.nodes`** is an insertion-ordered `dict` used as a set, matching the ordering
  guarantee of the reference's `Set` (Python's `set` iterates in hash order).
- **`SymbolIds`** wraps a `dict` rather than subclassing it: `set(key, value, pos)` keeps
  the extra position argument, and `reverse_get`, `get_pos` and `items()` mirror the
  reference's API.
- **`Pointers`/`ParseState`/`Graph` privates** use a single leading underscore where the
  reference uses `#` fields.
- **Time limit.** `RulesBuilder`'s limit stays in seconds (`performance.now() / 1000` →
  `time.perf_counter()`), so the default of `1000` means the same thing.
- **`get_serialized_rule_key`** passes `separators=(",", ":")` to `json.dumps`, so its
  keys are byte-identical to the reference's `JSON.stringify` ones. They are internal to
  graph construction either way.
- **`validate_non_empty`** is exported but never called, as in the reference.
