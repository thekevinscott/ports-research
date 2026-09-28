# 2026-09-27T23:14Z grammars inlined into the python suite, no fixture copy

Follows the 12:40Z entry. PR #78 carried a patch that made the python
`write_integration_tests` target copy `test/iteration/grammars/` beside the
generated suite, because the python template for `grammars.md` read the
fixtures from disk at test time. Kevin: "I _really_ don't like patch 0003.
How does typescript do it? How come they don't need the grammars copied?"

## Why typescript never needed the copy

`grammars.md` defines its cases in a javascript block that globs the fixture
directory while test-writer is running and returns an array of name, input,
grammar. For a javascript target `hydrateVariables` inlines that array as
JSON, so the generated suite carries every grammar as a string literal and
the fixture directory is done with at write time.

For a python target the same function pasted the block's source text
instead, which is right for a python cases block and garbage for a javascript
one. That one branch was the reason for the disk read and the copy.

## What replaced it

Patch 0001 now fixes test-writer: paste source only when the block is python,
JSON-encode otherwise. A JSON array of strings is a python literal. The python
template in 0002 is a mirror of the typescript one, `$cases_three` and an
`unescape` helper, and the copy line is gone from the Makefile patch, now
0004. The grammar fixture files leave the eight python listings.

Making that work turned up a second test-writer fault. `formatPython` fed the
generated code to black through a triple-quoted string after a hand escape of
quotes and backslash-n, and that escape turned an escaped newline into a line
continuation. The inlined grammars hit it at once; the existing python suites
had been quietly losing `\n` from three grammars since the pin. Passing the
code as a JSON string literal fixes both. Three lines in the shipped python
suites change, each back to what the markdown says. That is a change to a
suite upstream ships, recorded here so it is not mistaken for an upstream
fact.
