# porting-harness

Ports a reference library into another language, using agent-harness-sandbox.

`run_porting_harness` takes a prompt, an input directory and an output
directory. The input is one folder, handed to the image build as the `input`
build context: `modify_dockerfile` is where the caller copies it to `/input`,
so its dependencies can be installed while the network is still open. Nothing
is mounted at `/input` — a bind there would shadow what the build wrote. The
output directory mounts writable at `/target` and is the port as the agent
leaves it.

The harness owns a system prompt, `prompt.txt`, that frames the task: the
reference is at `/input`, the port goes to `/target`. The caller's prompt is
appended to it, and only the caller can describe the folder it laid out: what
is the source, what is a suite, what to port to.

Library only, no CLI. Generic: knows nothing about gbnf. Does not produce
tests and does not grade the result.

Depends on agent-harness-sandbox.
