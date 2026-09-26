# gbnf-experiment

Configures porting-harness for one library: [gbnf](https://github.com/thekevinscott/gbnf),
which has TypeScript and Python implementations sharing one test suite.

## Preparing the reference

The prepare image in `docker/gbnf-prepare/` does four things, at build time:

1. Clones gbnf at the pinned commit.
2. Applies `patches/` and commits them.
3. Installs node modules and builds test-writer.
4. Runs test-writer for each language, producing the generated test suites.

The result is a tree of source and tests per language.

## Running

CLI `run-gbnf-experiment`. Each invocation is one experimental condition: a
source language, and whether each language's test suite is mounted alongside
the reference. It

- builds the prepare image;
- selects the reference files for the condition;
- hands them to porting-harness;
- writes one run directory under `data/runs/` holding the manifest, the
  result, the transcript and the proxy log.

Everything gbnf-specific lives here: the pin, the patches, the test
generation, the file selection. Analysis of the port happens elsewhere and is
not part of a run.

Depends on porting-harness.
