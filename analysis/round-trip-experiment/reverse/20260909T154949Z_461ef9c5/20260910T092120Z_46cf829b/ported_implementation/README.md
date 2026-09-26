# gbnf (TypeScript)

A TypeScript port of `../reference_implementation` — a library for parsing GBNF grammars and
walking the resulting graph one character at a time.

```ts
import GBNF from 'gbnf';

let state = GBNF('root ::= "foo"');
[...state];            // [{ type: 'char', value: [102] }]

state = state.add('f');
[...state];            // [{ type: 'char', value: [111] }]

state = state.add('oo');
[...state];            // [{ type: 'end' }]
```

`GBNF(grammar, initialString = '')` returns a `ParseState`. Iterating a `ParseState` yields
the rules that may match next (`RuleChar`, `RuleCharExclude`, `RuleEnd`); `state.add(input)`
returns a new `ParseState` advanced past `input`, or throws `InputParseError`. An invalid
grammar throws `GrammarParseError`. A `ParseState` is also callable, so `state('foo')` is
shorthand for `state.add('foo')`.

## Layout

The module tree mirrors the reference file-for-file:

| Python | TypeScript |
| --- | --- |
| `gbnf/__init__.py` | `src/index.ts` |
| `gbnf/gbnf.py` | `src/gbnf.ts` |
| `gbnf/rules_builder/*.py` | `src/rules-builder/*.ts` |
| `gbnf/grammar_parser/build_rule_stack.py` | `src/grammar-parser/build-rule-stack.ts` |
| `gbnf/grammar_graph/*.py` | `src/grammar-graph/*.ts` |
| `gbnf/utils/**/*.py` | `src/utils/**/*.ts` |

Two names differ: `grammar_graph/print_.py` is `grammar-graph/print.ts` (the trailing
underscore only existed to dodge the Python builtin), and `gbnf/valid_input.py` is
`src/valid-input.ts` — it stays a separate module for the same reason, so that
`utils/errors` does not have to import from `grammar-graph`. `src/grammar-graph/
types-internal.ts` is new: it holds the `RootNode`/`Pointers` aliases that `graph.py`
declared inline, so that `graph-node.ts` can name them without importing `graph.ts`.

## Tests

```sh
cd /workspace/ported_implementation
npx vitest run --config vitest.config.unit.ts
```

`tests/` is the generated suite from `/workspace/tests/typescript`, copied in as its README
directs; `vitest.config.unit.ts` aliases `gbnf` to `src/index.ts`. 773 tests, all passing.

`vitest` is installed globally on this image and is symlinked into `node_modules/` so that
the suite's `import ... from 'vitest'` resolves. There is no TypeScript compiler available
offline here, so `npm run typecheck` (`tsc --noEmit`) needs `npm i -D typescript` first;
vitest transpiles with esbuild and does not type check.

## Intentional deviations from the reference

* **Plain object rules.** The Python rules are classes with `as_dict()` and value equality.
  Here they are plain objects (`{ type: 'char', value: [...] }`), which is what the test
  suite compares against directly, and `Map<UnresolvedRule, ...>` lookups key on object
  identity — equivalent, because `Graph` collapses structurally identical rules onto a
  single instance before any lookup happens. `RuleRef` stays a class, as it carries the
  lazily assigned `nodes` set.
* **No `as_dict()`/`as_list()`.** Unneeded: the rules are already plain data.
* **`ValueError` becomes `Error`.** JS has no `ValueError`; the messages are unchanged.
* **Sparse rule arrays.** `RulesBuilder.rules` is indexed by symbol id and grows holes on
  out-of-order assignment, exactly as the original JS did; the Python padded with `None`
  instead. Reads of a hole yield `undefined`, which the validation pass and `Graph` skip.
* **Bounds-checked reads.** The Python helpers took an explicit `_at(pos)` accessor to
  emulate JS out-of-range indexing; here plain indexing gives `undefined` directly.
* **`parseChar` on astral characters.** The Python indexes by code point; JS indexes by code
  unit, so the unescaped branch advances by the code point's UTF-16 length rather than 1,
  keeping a surrogate pair one character.

## Verification

Beyond the ported suite, the port was differentially tested against the reference over 1116
cases — every grammar in the test fixtures plus malformed inline grammars, fed valid,
truncated, mutated and randomized inputs — comparing the rule set after each character, the
rendered `Graph.print()` output, and all error messages. The only differences are the
`ValueError`/`Error` class name above, and, for `root ::= "\xZZ"` (an escape with no hex
digits), the class of the error raised when printing the resulting graph: `parseInt` yields
`NaN` where Python's emulation yields `None`, so `String.fromCodePoint` throws a
`RangeError` where `chr` threw a `TypeError`. Both implementations fail on the same input at
the same point.
