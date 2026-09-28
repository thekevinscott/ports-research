# gbnf-experiment

Configures porting-harness for one library: [gbnf](https://github.com/thekevinscott/gbnf),
which has javascript and python implementations sharing one test suite.

CLI `run-gbnf-experiment`. Each invocation is one experimental condition: a
source language (`--source-language javascript|python`) and three independent
suite flags, `--include-unit-tests`, `--include-source-integration-tests` and
`--include-target-integration-tests`. Sixteen conditions. It

- builds the prepare image in `docker/` for that condition, which clones gbnf at
  the pinned commit, applies `patches/`, generates both test suites and
  assembles `/shared`: the `packages/gbnf` tree in upstream layout,
  `javascript/` and `python/`, filtered to the whitelist the condition composes;
- copies `/shared` out of the image into a temporary directory;
- hands that one directory to porting-harness, which mounts it read-only at
  `/input`;
- writes one run directory under `data/` holding the manifest, the result,
  the transcript and the proxy log.

The prompt is this package's, in `src/gbnf_experiment/prompt.txt`. porting-harness
slots it into its own system prompt, which frames the task and names the two
container paths: the reference at `/input`, the port at `/target`. The folder's
layout is decided here, so the description of it belongs here too. `render_prompt`
fills in the two language names, which are also the two directory names, and the
manifest banks the rendered text, unwrapped.

Everything gbnf-specific lives here: the pin, the patches, the test generation,
the file filter. All four are inside the image, so there is one place the corpus
is decided; the host selects nothing and the manifest records the listing it
reads back off the copied-out folder. Grading the port against the held-out
suite is a separate step and not part of a run.

Depends on porting-harness.
