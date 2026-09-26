# GBNF (TypeScript port)

A TypeScript port of `../reference_implementation` — a library for parsing `.gbnf` grammars
and walking a grammar graph one input character at a time.

```ts
import { GBNF } from './src/index.ts';

let state = GBNF('root ::= "foo"');
state = state.add('f');
for (const rule of state) {
  console.log(rule.toDict()); // { type: 'RuleChar', value: [111] }
}
```

## Layout

The module structure mirrors the Python reference one-to-one, with Python's `snake_case`
file and identifier names converted to TypeScript's `camelCase`:

| Python | TypeScript |
| --- | --- |
| `gbnf/GBNF.py` | `src/GBNF.ts` |
| `gbnf/rules_builder/` | `src/rulesBuilder/` |
| `gbnf/grammar_parser/` | `src/grammarParser/` |
| `gbnf/grammar_graph/` | `src/grammarGraph/` |
| `gbnf/utils/` | `src/utils/` |

Python constructs without a TypeScript equivalent are mapped as follows:

- Dataclasses become classes with public fields, so `assert.deepStrictEqual` distinguishes
  them by prototype the way Python's `isinstance`-based `__eq__` did.
- `__iter__` becomes `[Symbol.iterator]()`; `__len__` becomes a `size` getter.
- `ParseState.__call__` and `ParseState.__add__` are dropped — `parseState.add(text)` is the
  single way to advance a parse.
- `src/utils/repr.ts` reproduces Python's `repr()` and `json.dumps()` output formats so that
  error messages and serialized rule keys are byte-for-byte identical to the reference's.

## Intentional deviations

Three reference behaviours are bugs that the port fixes, because in each case the reference
crashes with a raw Python exception before reaching a guard it already contains:

1. A grammar without a `root` symbol raises `KeyError: 'root'` in the reference
   (`symbol_ids["root"]` throws before the `is None` check). The port raises the intended
   `GrammarParseError: Grammar does not contain a 'root' symbol`.
2. An unterminated group (`root ::= "a" (`) raises `IndexError` in the reference. The port
   raises the intended `GrammarParseError: Expecting ')' at ...`.
3. `Graph.print()` raises `AttributeError` in the reference for any `RuleEnd` node, because
   `print_graph_node` reads `rule.type`, which only exists inside `Rule.__dict__`. The port
   gives every rule a real `type` property, so printing a graph works.

Additionally, `parseChar` advances by two positions for an astral-plane character, since
JavaScript strings are indexed by UTF-16 unit where Python strings are indexed by code point.

## Tests

`test/` is a port of the reference's own unit tests, plus end-to-end fixtures captured from
the reference implementation. Run them with Node's built-in test runner:

```bash
npm test           # from the workspace root
node --test 'ported_implementation/test/**/*.test.ts'
```

No dependencies are required: the sources are executed directly via Node's TypeScript type
stripping (Node >= 22.6), which is why relative imports carry an explicit `.ts` extension.
