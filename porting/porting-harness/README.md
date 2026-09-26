# porting-harness

Ports a reference library into another language, using agent-harness-sandbox.

`run_porting_harness` takes a reference directory, a target language and an
output directory. The reference holds the source tree under `source/` and,
optionally, test suites under `tests/`. Each mounts read-only; `tests/` is not
mounted when absent. The output directory mounts writable and is the port as
the agent leaves it.

The prompt is this package's own, `src/porting_harness/prompt.txt`, rendered
for the target language. Callers say what to port and where to. They never
phrase the request, so every run gets the same wording.

Library only, no CLI. Generic: knows nothing about gbnf. Does not produce
tests and does not grade the result.

Depends on agent-harness-sandbox.
