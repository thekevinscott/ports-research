# Porting notes

The port is behaviour-for-behaviour with `reference_implementation/`, verified by
differential tests against fixtures generated from the Python code itself
(`test/differential.test.ts`). This file records everywhere the two intentionally differ,
and the language-level decisions that needed making.

## Reference bugs that are fixed here

Each of these is a case where the Python code crashes with an error it clearly did not
intend, and where the intended behaviour is stated in the Python source itself.

1. **`Graph.print()` crashes on any real grammar.** `print.py` falls back to
   `col(rule.type, ...)`, but `Rule` only exposes `type` inside its `__dict__` property,
   so `rule.type` raises `AttributeError: 'RuleEnd' object has no attribute 'type'`. Every
   graph contains `RuleEnd` nodes, so `print()` never succeeds. Here `Rule.type` is a real
   getter returning the class name (the same value `__dict__` reports), and printing works:
   `{0,0,0}[f]-> {0,0,1}[o]-> {0,0,2}[o]-> {0,0,3}RuleEnd`.

2. **A grammar with no `root` symbol raises `KeyError`.** `GBNF.py` checks
   `if symbol_ids["root"] is None`, but `SymbolIds.__getitem__` raises `KeyError` for a
   missing key, so the `GrammarParseError("Grammar does not contain a 'root' symbol")` on
   the next line is unreachable. The port raises that `GrammarParseError`.

3. **Unterminated constructs raise `IndexError`.** `root ::= "foo`, `root ::= [a-z` and
   `root ::= ("a"` all walk off the end of the grammar string in Python. In TypeScript the
   same code paths reach `parseChar`'s own bounds check, or the `Expecting ')'` check, so
   they raise `GrammarParseError` with a position marker.

4. **`build_error_position` can index past the end of its line list.** For a position
   beyond the end of a multi-line source (e.g. `build_error_position("aa\nbb\ncc", 7)`)
   Python raises `IndexError`. The port stops at the last line and renders the caret there.

Everything else — including every error message, `symbol_ids` numbering, rule ordering and
parse-state content — matches the reference exactly.

## Language-level decisions

- **Code points, not UTF-16 units.** Python indexes strings by code point; JavaScript by
  UTF-16 code unit. Every position and length in this library is a code point index, so
  the parsers walk `Array.from(src)` (`src/utils/code-points.ts`). Without this, a grammar
  or input containing an astral character (`root ::= "💩"`) would desynchronise.
- **Equality.** Python's `__eq__` overloads (`Rule`, `InternalRuleDef*`,
  `GrammarParseError`, `InputParseError`) cannot be expressed in JavaScript. The classes
  are plain data holders, so structural comparison (`assert.deepEqual`) gives the same
  result, and identity comparison is used where the reference relies on it — notably
  `Graph.iterateOverPointers`, whose `OrderedDict` is keyed on `Rule.__hash__ = id(self)`.
- **`Rule.toJSON()`** returns the same shape as Python's `Rule.__dict__`
  (`{ type, value }`), which is what `ParseState.rules()` de-duplicates on.
- **`getSerializedRuleKey`** uses `JSON.stringify` where Python uses `json.dumps`; the
  keys differ in whitespace only (`1-[97,122]` vs `1-[97, 122]`) and are internal to graph
  construction.
- **Time limit.** `RulesBuilder`'s limit stays in seconds (`perf_counter()` →
  `performance.now() / 1000`), so the default of `1000` means the same thing.
- **`SymbolIds`** extends `Map`, so `get`/`has`/`size`/iteration are the native ones;
  `set(key, value, pos)` keeps the extra position argument, and `reverseGet`, `getPos` and
  `items()` mirror the Python API.
- **`ParseState`/`Graph` privates** use `#` fields; the reference's `__foo__` names are not
  private in Python, so its "private" methods are public here (see README).

## Quirks preserved on purpose

- `Graph`'s `unique_rules` map is written and immediately read back with the same key, so
  it never actually de-duplicates anything. Preserved — node/rule identity affects
  `iterateOverPointers` grouping.
- `Graph.iterateOverPointers` pushes the first pointer of each group twice. Preserved; it
  only means `setValid` writes the same pointer twice.
- `Graph.add` treats an empty `Pointers` as "no pointers given" and falls back to the
  initial pointers, matching Python's truthiness rules for `__len__`.
- `validateNonEmpty` is exported but never called — in the reference it is only referenced
  as unused dataclass field metadata.
