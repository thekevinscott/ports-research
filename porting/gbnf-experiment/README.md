# gbnf-experiment

Configures porting-harness for one library: [gbnf](https://github.com/thekevinscott/gbnf),
which has javascript and python implementations sharing one test suite.

CLI `run-gbnf-experiment`. Each invocation is one experimental condition: a
source language, and whether each language's test suite is mounted alongside
the reference. It

- builds the prepare image in `docker/`, which clones gbnf at the pinned
  commit, applies `patches/`, and generates the test suites;
- selects the reference files for the condition;
- hands them to porting-harness;
- writes one run directory under `data/` holding the manifest, the result,
  the transcript and the proxy log.

Everything gbnf-specific lives here: the pin, the patches, the test
generation, the file selection. Grading the port against the held-out suite
is a separate step and not part of a run.

Depends on porting-harness.
