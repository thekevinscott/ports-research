# Patches

Every file in this directory ending in `.patch` is applied to the gbnf clone, in name order, with `git apply`, right after the checkout at the pinned commit and before anything is built. They are the only edits made to gbnf. Each one is a plain `git format-patch` diff against the pin, small enough to read as a diff.

A patch is added when the experiment needs gbnf to be something it is not at the pin. It is not added to fix a gbnf bug; bugs are experiment input. Changing this directory changes the prepared image, so every run records the pin and the patches that shaped it.

## 0001-test-writer-emit-JSON-for-non-python-cases-blocks-an

Two fixes in test-writer, the tool gbnf uses to render its markdown test specs into per-language suites. Neither changes a suite gbnf ships today except to restore text the spec author wrote.

`hydrateVariables` substitutes a `$cases` variable with the value of the named code block. For a python target it pasted the block's source text whatever language the block was, so `grammars.md`, whose only cases block is javascript, could not render a python suite. It now pastes source only when the block is python and JSON-encodes the value otherwise. A JSON array of strings is a python literal.

`formatPython` wrapped the generated code in a triple-quoted string after a hand escape of quotes and backslash-n. That escape turned an escaped newline into a line continuation, so a grammar written as `"\\n"` reached the generated suite with the newline gone. The code is now passed as a JSON string literal. Three lines in the existing python suites change as a result, each back to what the markdown says.

## 0002-Add-python-template-to-grammars.md-test-suite

`packages/gbnf/test/iteration/grammars.md` is the one test-spec file with a typescript template and no python one. The patch adds the python template as a mirror of the typescript one: `$cases_three` is the same inlined array of name, input and grammar, and an `unescape` helper undoes the escaping the cases block applied. The generated suite carries every grammar as a string literal, as the typescript suite does, so nothing is read from disk at test time.

## 0003-Drop-the-builder-re-exports-from-the-javascript-inde

`src/builder/` is a grammar-authoring DSL with no counterpart to port, so the whitelist withholds it. `src/index.ts` re-exported it, and a reference that re-exports a directory it does not contain fails to typecheck. The patch removes the two re-exports. Before this, a regex edited the copy per run.

## 0004-Generate-every-python-suite

`make write_integration_tests` in the python package named the suites it wanted, `validation` and `iteration/iteration`, which skipped `grammars.md` because at the pin it had no python template. 0002 gives it one, so the patch drops the list and the target writes every suite, six files, the same set as typescript. Kevin, 2026-09-27: "I want python to use grammars.md."
