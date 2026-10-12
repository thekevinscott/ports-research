# gbnf_experiment

Configures port_codebase for one library: [gbnf](https://github.com/thekevinscott/gbnf), which has javascript and python implementations sharing one test suite.

CLI `run_gbnf_experiment`. Each invocation is one experimental condition: a source language, and whether the source's unit tests, the source's integration tests and the target's integration tests are included. It

- builds the prepare image in `docker/` for the condition: it clones gbnf at the pinned commit, applies `patches/`, generates both integration suites, and copies into `/shared` the files the condition's `RULES` admit, in gbnf's upstream layout (`javascript/`, `python/`);
- extracts `/shared` to a cache entry keyed on the commit, `docker/` and `RULES`, one per condition;
- hands that tree unchanged as the source, with a prompt and a `ClaudeAgent`, to `port_codebase`;
- banks the `RunResult` as one run directory under `data/`: `manifest.json` (with the agent's `exit_code`), `result.json` (the agent CLI's stdout), `stderr.txt` (its stderr), `transcript/` (the transcript files, at their paths relative to the agent's home), `proxy.log`.

The prompt names the source as `javascript/` or `python/`, the target language (`javascript` reads as `typescript`), the installed tools, and where each included suite sits. Paths in it are relative to the source directory.

```
uv run run_gbnf_experiment --source-language python --include-unit-tests --include-source-integration-tests --include-target-integration-tests
```

| Flag | What it is |
| --- | --- |
| `--source-language` | `javascript` or `python`. The port goes to the other. |
| `--include-unit-tests` | Include the source's unit tests, beside the modules they test. |
| `--include-source-integration-tests` | Include the source's generated integration suite. |
| `--include-target-integration-tests` | Include the target's generated integration suite. |
| `--model` | Passed to `ClaudeAgent`. Default `claude-opus-5`. |
| `--effort` | Passed to `ClaudeAgent`. Default `high`. |
| `--debug` | Show the prepare image's build output. |

Everything gbnf-specific lives here: the pin, the patches, the test generation, the rules. Grading the port against the held-out suite is a separate step and not part of a run.

A run that raises still writes `manifest.json` with the error, then re-raises.

Depends on port_codebase and botbox.

## Running the matrix

`scripts/run_matrix.py` runs `run_gbnf_experiment` through the SDK over cells: source language × the 8 combinations of the three test flags × four models (Opus 5.5, Sonnet 5.5, Fable 5.1, Haiku 4.5) × each effort in `--efforts`. 64 cells per effort.

```
uv run --env-file ../../.env python scripts/run_matrix.py --parallel 2 --efforts low,xhigh
```

It exits before doing anything if `ANTHROPIC_API_KEY` is unset or empty. The key goes to `ClaudeAgent(api_key=)`; subscription credentials are never used.

It first prepares all 16 conditions one at a time, since concurrent prepares of one condition collide. Then each round runs every cell once in a fresh shuffled order, `--parallel` at a time, until `--n` rounds are done or it is stopped.

Each finished run appends one line to `data/runs/matrix-<UTC timestamp>.jsonl`: the cell, the round, the run directory or the error, `exit_code`, wall seconds and `result.json`'s `usage`. A run that raises is recorded and the loop continues.

Ctrl-C starts no new runs and waits for the in-flight ones to finish and be recorded. Runs ignore SIGINT, as do their docker subprocesses.

`--efforts` is comma-separated; omitted, every cell runs at the claude CLI's default effort. `--models`, `--source-languages` and `--cells` (the manifest's condition name, as printed per run, e.g. `source-python_unit-tests_effort-low_model-claude-haiku-4-5-20251001`) restrict the cells.
