# GBNF — TypeScript port

A TypeScript port of the Python reference implementation in
`../reference_implementation`: a library for parsing `.gbnf` grammar files and
incrementally validating input against them.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

let state = GBNF(`
root  ::= "yes" | "no"
`);
```

If the grammar is invalid, `GBNF` throws a `GrammarParseError`.

`GBNF` returns a state representing the parsed state, which is iterable:

```ts
for (const rule of state) {
  console.log(rule);
  // { type: 'char', value: [121] }   -> 'y'.codePointAt(0)
  // { type: 'char', value: [110] }   -> 'n'.codePointAt(0)
}
```

`state` cannot be indexed directly, but can be spread into an array with
`[...state]` and indexed that way.

States are *immutable*. To parse a new token, call `state.add()`:

```ts
let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]);   // [{ type: 'char', value: [73] }]  -> 'I'
state = state.add('I li');
console.log([...state]);   // [{ type: 'char', value: [107] }] -> 'k'
state = state.add('ke gree');
console.log([...state]);   // [{ type: 'char', value: [110] }] -> 'n'
```

The state is also callable — `state('I li')` is the same as `state.add('I li')`.

The possible rules returned are:

- `RuleChar` (`RuleType.CHAR`) — `value` holds code points to match, or two-element
  `[start, end]` tuples denoting an inclusive range.
- `RuleCharExclude` (`RuleType.CHAR_EXCLUDE`) — code points or ranges *not* to match.
- `RuleEnd` (`RuleType.END`) — denotes a valid end of a string.

Rules are plain objects with a `type` and (except for `RuleEnd`) a `value`, so they
compare equal to their literal form:

```ts
expect([...GBNF('root ::= "a"')]).toEqual([{ type: 'char', value: [97] }]);
```

Input can be a string, a single code point, or an array of code points
(`ValidInput = string | number | number[]`). Input that the grammar cannot accept
throws an `InputParseError`.

## Importing

The package entry point is `src/index.ts`, which exports `GBNF` both as the default
and as a named export, alongside `ParseState`, `RuleType`, `isRange`,
`GrammarParseError`, `InputParseError` and the rule types.

There is no build step: the package is consumed as TypeScript source (`main` and
`types` both point at `src/index.ts`), so relative imports carry explicit `.ts`
extensions. That works with bundlers/vitest and lets Node run the sources directly
via type stripping (`node --experimental-strip-types`); `tsc` needs
`allowImportingTsExtensions`, which `tsconfig.json` sets.

## Layout

The port mirrors the reference file-for-file, with names converted to `kebab-case`
files and `camelCase` identifiers:

| reference (Python)                        | port (TypeScript)                          |
| ----------------------------------------- | ------------------------------------------ |
| `gbnf/gbnf.py`                            | `src/gbnf.ts`                              |
| `gbnf/__init__.py`                        | `src/index.ts`                             |
| `gbnf/grammar_graph/*.py`                 | `src/grammar-graph/*.ts`                   |
| `gbnf/grammar_parser/build_rule_stack.py` | `src/grammar-parser/build-rule-stack.ts`   |
| `gbnf/rules_builder/*.py`                 | `src/rules-builder/*.ts`                   |
| `gbnf/utils/**/*.py`                      | `src/utils/**/*.ts`                        |

`src/utils/code-points.ts` has no reference equivalent; it holds the helpers that
keep string handling code-point based (see the notes below).

## Tests

```sh
npx vitest run --config vitest.config.unit.ts     # 773 tests
```

`tests/` is the generated suite from `/workspace/tests/typescript`, and
`vitest.config.unit.ts` aliases `gbnf` to `src/index.ts`.

The port was additionally checked against the reference implementation directly,
using the reference's own differential harness
(`reference_implementation/tests/differential/run_reference.ts`, which loads
`<dir>/gbnf.ts` and dumps one JSON result per case):

```sh
node --experimental-strip-types \
  reference_implementation/tests/differential/run_reference.ts \
  ported_implementation/src reference_implementation/tests/corpus.json
python3 reference_implementation/tests/differential/run_ported.py \
  reference_implementation/tests/corpus.json
```

The two outputs are identical over the reference's 75-case corpus and its 510
seeded fuzz cases — emitted rules, state size, the rendered graph (plain and
ANSI-colored), and the exact error type and message, for every input.

### Notes on the translation

- Rules (`RuleChar`, `RuleCharExclude`, `RuleEnd`) are plain object literals rather
  than classes, the shape the reference's `to_dict()` describes. Every distinct rule
  is de-duplicated to a single object when the graph is built, so identity
  comparison (JS `Map`/`Set`) groups them exactly as the reference's value-based
  comparison does.
- Python `dict`s become JS `Map`s and `Set`s, which preserve insertion order the
  same way, so rule ordering matches. `RuleRef.nodes` is an ordered, de-duplicated
  array for the same reason.
- `GraphNode`, `GraphPointer` and `RuleRef` are identity-compared, as in the
  reference.
- `RulesBuilder.rules` is a sparse array indexed by rule id; holes read back as
  `undefined` and are skipped during validation, matching the reference's
  `None`-padded list.
- `ParseState.__call__` becomes the `extends Function` + `Proxy` trick, so
  `state(input)` still works; `__repr__` methods become `toString`.
- The `RuleType`, `InternalRuleType` and `Color` enums are `as const` objects plus a
  matching type, so the source stays fully erasable (no TS `enum`).
- Strings are treated as sequences of **code points**, not UTF-16 code units, which
  is what the reference does. `src/utils/code-points.ts` supplies `toChars`,
  `codePointLength` and `at`; the grammar is indexed as a code-point array, so
  grammar offsets, error carets and input positions all agree with the reference for
  astral characters as well as the BMP (verified against it, including
  `\U0001F600`-style escapes).
- Malformed hex escapes throw a `GrammarParseError` naming the bad escape rather
  than yielding a `NaN` code point, matching the reference. `parseInt` is only
  reached after the slice is checked against `/^[0-9a-fA-F]+$/`, so the strings
  Python's `int(raw, 16)` would reject are rejected here too.
- A grammar with no `root` symbol throws `GrammarParseError`, matching the
  reference (which documents this as its one intentional deviation from the
  original TypeScript, where the branch was unreachable).
