# Patches

Every file in this directory ending in `.patch` is applied to the gbnf clone, in name order, with `git apply`, right after the checkout at the pinned commit and before anything is built. They are the only edits made to gbnf. Each one is a plain `git format-patch` diff against the pin, small enough to read as a diff.

A patch is added when the experiment needs gbnf to be something it is not at the pin. It is not added to fix a gbnf bug; bugs are experiment input. The tests in particular are not patched ahead of a run. Kevin, 2026-09-27: "Let them fail. Let's see them fail, and let's fix them when they fail and we can see how they fail." Changing this directory changes the prepared image, so every run records the pin and the patches that shaped it.

## 0001-Drop-the-builder-re-exports-from-the-javascript-index

`src/builder/` is a grammar-authoring DSL with no counterpart to port, so the whitelist withholds it. `src/index.ts` re-exported it, and a reference that re-exports a directory it does not contain fails to typecheck. The patch removes the two re-exports. Before this, a regex edited the copy per run.
