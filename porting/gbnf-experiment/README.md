# gbnf-experiment

Configures porting-harness for one library: [gbnf](https://github.com/thekevinscott/gbnf),
which has TypeScript and Python implementations sharing one test suite.

CLI `run-gbnf-experiment`. Each invocation is one experimental condition: a
source language, and whether each language's test suite is mounted alongside
the reference. It

- builds the prepare image in `docker/` for that condition, which clones gbnf at
  the pinned commit, applies `patches/`, generates the flagged test suites and
  assembles `/reference`;
- copies `/reference` out of the image into a temporary directory;
- hands that directory to porting-harness;
- writes one run directory under `data/` holding the manifest, the result,
  the transcript and the proxy log.

Everything gbnf-specific lives here: the pin, the patches, the test generation,
the file filter. All four are inside the image, so there is one place the corpus
is decided; the host selects nothing and the manifest records the listing it
reads back off the copied-out folder. Grading the port against the held-out
suite is a separate step and not part of a run.

Depends on porting-harness.
