# gbnf (Python)

A Python port of `reference_implementation/` (the TypeScript `gbnf` package).

```py
from gbnf import GBNF

state = GBNF('root ::= "foo"')
state = state.add("f")
[*state]  # [RuleChar([111])]
```

`GBNF(grammar, initial_string="")` builds the grammar graph and returns a `ParseState`.
Iterating a `ParseState` yields the deduplicated set of rules that may match next
(`RuleChar` / `RuleCharExclude` with a `value`, or `RuleEnd`). `state.add(text)` — also
spelled `state + text` — advances the parse and returns a new `ParseState`, raising
`InputParseError` when the text cannot be matched; invalid grammars raise
`GrammarParseError`.

## Layout

The module layout mirrors the reference implementation, with TypeScript `kebab-case`
filenames rendered as `snake_case`:

| TypeScript | Python |
| --- | --- |
| `src/GBNF.ts` | `gbnf/GBNF.py` |
| `src/index.ts` | `gbnf/__init__.py` |
| `src/grammar-graph/*` | `gbnf/grammar_graph/*` |
| `src/grammar-parser/*` | `gbnf/grammar_parser/*` |
| `src/rules-builder/*` | `gbnf/rules_builder/*` |
| `src/utils/*` | `gbnf/utils/*` |

Notable translations:

- The tagged rule objects (`{ type: RuleType.CHAR, value }`) become small classes with
  `type`/`value` attributes and value equality, so tests can compare them directly and
  `build_rule_stack` can still mutate `value` in place. `RuleRef` keeps its lazily
  patched `nodes`.
- JS generators, `Map`, and `Set` map to Python generators and `dict` — all insertion
  ordered, which is what fixes the order rules are yielded in. `Pointers` and
  `SymbolIds` wrap dicts; `Graph._iterate_over_pointers` keys on `id(rule)` to mirror
  a `Map` keyed by rule object identity.
- TypeScript's type guards become `getattr(rule, "type", None)` checks, so passing
  `None` (JS `undefined`) is still safe.
- `char_at()` reproduces JS's out-of-bounds string indexing, which the parser relies on
  for lookahead; plain `src[pos]` is kept where the position is already bounds checked.
- The type checks that TypeScript performs at runtime (`typeof x !== 'string'`) raise
  `TypeError`; the other `Error` throws become `ValueError`.
- `GrammarParseError` compares by `(grammar, pos, reason)` and `InputParseError` by
  rendered message, since the raised error carries code points where a caller-built
  expectation carries the equivalent string.

One intentional behavioral difference: the reference walks the grammar source by UTF-16
code unit, so a non-BMP literal inside a character class (`root ::= [😀-😎]`) is split
into surrogate halves. Python strings are sequences of code points, so the port reads
that as the single range it denotes. Every other grammar and input tested matches the
reference exactly.

## Tests

```sh
cp -r /workspace/tests/python tests
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```
