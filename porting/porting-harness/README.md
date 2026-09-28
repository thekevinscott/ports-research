# porting-harness

Ports a reference library into another language, using agent-harness-sandbox.

`run_porting_harness` takes a prompt, a reference directory and an output
directory. The reference is one folder, mounted read-only at `/input`. The
caller lays it out and the caller's prompt describes it: what is the source,
what is a suite, what to port to. The harness adds no words. The output
directory mounts writable and is the port as the agent leaves it.

Library only, no CLI. Generic: knows nothing about gbnf. Does not produce
tests and does not grade the result.

Depends on agent-harness-sandbox.
