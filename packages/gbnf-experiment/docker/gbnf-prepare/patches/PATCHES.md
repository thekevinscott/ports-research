# Patches

Every file in this directory ending in `.patch` is applied to the gbnf clone, in name order, with `git apply`, right after the checkout at the pinned commit and before anything is built. They are the only edits made to gbnf. Each one is a plain `git format-patch` diff against the pin, small enough to read as a diff.

A patch is added when the experiment needs gbnf to be something it is not at the pin. It is not added to fix a gbnf bug; bugs are experiment input. Changing this directory changes the prepared image, so every run records the pin and the patches that shaped it.

## 0001-Add-python-template-to-grammars.md-test-suite

`packages/gbnf/test/iteration/grammars.md` is the one test-spec file with a typescript template and no python one, so test-writer rendered a python suite missing the grammar-fixture cases. The patch adds the python template: it loads every `.gbnf` under `iteration/grammars/`, pairs it with its `.json` case list, and feeds each case through `GBNF(...).add(char)`. This is the reason the python suite ships with that fixture directory.

## 0002-Drop-the-builder-re-exports-from-the-javascript-index

`src/builder/` is a grammar-authoring DSL with no counterpart to port, so the whitelist withholds it. `src/index.ts` re-exported it, and a reference that re-exports a directory it does not contain fails to typecheck. The patch removes the two re-exports. Before this, a regex edited the copy per run.
