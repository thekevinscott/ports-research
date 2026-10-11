# gbnf_experiment

Configures port_codebase for one library: [gbnf](https://github.com/thekevinscott/gbnf), which has javascript and python implementations sharing one test suite.

CLI `run_gbnf_experiment`. Each invocation is one experimental condition: a source language, and whether the source's unit tests, the source's integration tests and the target's integration tests are included. It

- builds the prepare image in `docker/` for the condition: it clones gbnf at the pinned commit, applies `patches/`, generates both integration suites, and copies into `/shared` the files the condition's `RULES` admit, in gbnf's upstream layout (`javascript/`, `python/`);
- extracts `/shared` to a cache entry keyed on the commit, `docker/` and `RULES`, one per condition;
- hands that tree unchanged as the source, with a prompt and a `ClaudeAgent`, to `port_codebase`;
- banks the `RunResult` as one run directory under `data/`: `manifest.json` (with the agent's `exit_code`), `result.json` (the agent CLI's stdout), `stderr.txt` (its stderr), `transcript/` (the transcript files, at their paths relative to the agent's home), `proxy.log`.

The prompt names the source as `javascript/` or `python/`, the target language, the package manager, and where each included suite sits. Paths in it are relative to the source directory.

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
