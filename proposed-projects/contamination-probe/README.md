# contamination-probe

Produces a semantically identical but textually unfamiliar copy of a reference
implementation — the library renamed, every public symbol renamed, the file layout
reshuffled — so that porting the copy instead of the original tests whether a model is
translating the grammar or recalling a memorized port of `gbnf` from its training data.

This package only produces the perturbed tree. It does not run a port against it.

```
uv run perturb-reference-tree \
  --source <path to the tree root containing gbnf/> \
  --output <output dir> \
  --library-name gbnf \
  --seed 0
```

`--source` is the tree root (the directory *containing* `gbnf/`, `pyproject.toml`, etc.),
not the package directory itself.

To probe for contamination, feed `<output dir>` into `porting-harness` as the source tree
in place of the real reference implementation. A separate grading suite that imports the
library by its old name is untouched by the perturbation — rope only rewrites imports it
can resolve, and by the time symbols are renamed the old library name no longer exists on
disk for an external file to resolve against. `<output dir>/rename-manifest.json` records
the full `{library_name: {old, new}, symbols: {old: new, ...}}` mapping for that seed, so a
caller can apply it to a grading suite's imports independently before comparing pass rates.

## Known limitations of the underlying tool (rope)

Two collateral effects were found and deliberately left unfixed, rather than patched with
hand-rolled string replacement:

- `unittest.mock.patch("dotted.string.path")` targets are resolved at runtime via
  `importlib`, with no static reference for any refactoring tool to trace. Source files
  that mock a collaborator by its pre-rename dotted path break after perturbation. Found in
  6 of gbnf's colocated test files; the derived (773-test) suite does not use `mock.patch`
  and is unaffected.
- Rope's collateral string-literal rename (`docs=True`) only touches files that already
  contain a real traceable reference to the renamed symbol, and renames every
  same-spelled string in such a file — including ones that are coincidentally, not
  semantically, connected. Found once: a dict key coincidentally spelled the same as a
  renamed function was renamed at its construction site but not at a distant read site,
  producing a `KeyError` at runtime.

Both are genuine gaps in rope, not bugs in this package's use of it.
