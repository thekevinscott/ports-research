# GBNF (TypeScript)

A TypeScript port of `reference_implementation/` — a library for parsing `.gbnf` grammar
files.

## Usage

Pass your grammar to `GBNF`:

```ts
import GBNF from 'gbnf';

const state = GBNF('root  ::= "yes" | "no"');
```

If the grammar is invalid, `GBNF` throws `GrammarParseError`.

`GBNF` returns a state representing the parsed state:

```ts
for (const rule of state) {
  console.log(rule);
  // { type: 'char', value: [121] }  -- 'y'
  // { type: 'char', value: [110] }  -- 'n'
}
```

`state` is iterable (you can also call `state.rules()` directly). It cannot be indexed,
but spreads into an array with `[...state]`.

States are _immutable_. To parse a new token, call `state.add()`:

```ts
let state = GBNF('root ::= "I like green eggs and ham"');
console.log([...state]);   // [{ type: 'char', value: [73] }]
state = state.add('I li');
console.log([...state]);   // [{ type: 'char', value: [107] }]
state = state.add('ke gree');
console.log([...state]);   // [{ type: 'char', value: [110] }]
```

A `ParseState` is also callable, so `state('I li')` is the same as `state.add('I li')`.

The possible rules returned are:

- `RuleChar` (`type === RuleType.CHAR`) — holds an array of code points to match, where an
  entry may itself be a two-element array denoting an inclusive range.
- `RuleCharExclude` (`type === RuleType.CHAR_EXCLUDE`) — the same, for code points _not_ to
  match.
- `RuleEnd` (`type === RuleType.END`) — denotes a valid end of a string.

If input does not match the grammar, `add` throws `InputParseError`.

## Layout

The module tree mirrors the reference tree one-for-one, with names converted from
snake_case back to kebab-case and identifiers to camelCase
(`gbnf/grammar_graph/graph_pointer.py` → `src/grammar-graph/graph-pointer.ts`).

## Notable differences from the reference

These are the places where a literal transcription was not possible or not correct:

- **Rules are object literals, not classes.** The Python reference models `RuleChar` /
  `RuleCharExclude` / `RuleEnd` as classes so `isinstance` can stand in for a structural
  type guard, and gives them a `.to_dict()` that produces the shape a TypeScript
  implementation returns. Here that shape _is_ the rule, and the type guards discriminate
  on `type`. `RuleRef` stays a class, because it carries lazily-assigned `nodes`.
- **Identity sets are real identity sets.** `GenericSet` and `Graph`'s
  `iterateOverPointers` key on `id()` in Python, because rules there define value equality
  and are therefore unhashable. `Set`/`Map` already key on object identity, so the `id()`
  indirection is gone. Iteration order is insertion order in both languages.
- **`GraphPointer.resolve` / `fetchNext` stay iterative.** The Python port made these
  iterative because a pointer's parent chain grows with every repetition of a
  self-referential rule. The same limit applies to the JavaScript call stack, so the
  explicit stack is kept. Yield order is unchanged.
- **`ParseState` callability.** Python defines `__call__`; here the class extends
  `Function` and the constructor returns a `Proxy` with an `apply` trap. Its fields are
  ordinary properties rather than `#private` ones, since private fields are not reachable
  through a proxy's `this`.
- **String indexing.** Python raises on an out-of-range string index while JavaScript
  yields `undefined`. `rulesBuilder.charAt` is kept anyway, narrowing both to `''`, so the
  character comparisons stay total and read the same as the reference.
- **Code points vs. UTF-16.** Python indexes strings by code point. `parseChar` therefore
  reads a full code point (`codePointAt`) and advances the cursor by that character's
  width in UTF-16 units, and `getInputAsCodePoints` iterates the string rather than its
  UTF-16 units. An astral character is one rule and one input step, as in the reference.
- **Sparse rule arrays.** `RulesBuilder.rules` pads with `undefined` where the Python pads
  with `None`; `buildRuleStack` and the undefined-rule validation treat that as a hole.
- **Error subclassing.** `GrammarParseError` and `InputParseError` call
  `Object.setPrototypeOf` so `instanceof` holds regardless of downlevel emit.

## Tests

```sh
cd /workspace/ported_implementation
npx vitest run --config vitest.config.unit.ts
```

`tests/` contains:

- `validation/`, `iteration/` — the generated suite copied verbatim from
  `/workspace/tests/typescript`, along with its `vitest.config.unit.ts` (copied to the
  package root, where it aliases `gbnf` to `src/index.ts`).
- `rules-builder.test.ts` — the reference's own rules-builder case table, taken from
  `reference_implementation/tests/fixtures/reference-cases.json` and copied to
  `tests/fixtures/`. It pins the exact internal rule definitions the parser emits, so it
  checks the port against the reference's internals rather than only its public API.

There is no lockfile and the registry is unreachable, so `node_modules/vitest` is a symlink
to the globally installed copy:

```sh
mkdir -p node_modules && ln -sfn /usr/local/lib/node_modules/vitest node_modules/vitest
```
