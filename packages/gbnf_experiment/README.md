# gbnf_experiment

Configures port_codebase for one library: [gbnf](https://github.com/thekevinscott/gbnf), which has javascript and python implementations sharing one test suite.

CLI `run_gbnf_experiment`. Each invocation is one experimental condition: a source language, and whether the source's unit tests, the source's integration tests and the target's integration tests are included. It

- builds the prepare image in `docker/` for the condition: it clones gbnf at the pinned commit, applies `patches/`, generates both integration suites, and copies into `/shared` the files the condition's `RULES` admit, in gbnf's upstream layout (`javascript/`, `python/`);
- extracts `/shared` to a cache entry keyed on the commit, `docker/` and `RULES`, one per condition;
- hands that tree unchanged as the source, with a prompt and a `ClaudeAgent`, to `port_codebase`;
- banks botbox's output into `--output`: `manifest.json` (with the agent's `exit_code`), `result.json` (the agent CLI's stdout), `stderr.txt` (its stderr), `transcript/` (the transcript files, at their paths relative to the agent's home), `proxy.log`.

The prompt names the source as `javascript/` or `python/`, the target language (`javascript` reads as `typescript`), and where each included suite sits. Paths in it are relative to the source directory.

It writes into `--output`, and exits non-zero when the agent exits non-zero, the result has `is_error`, or the manifest has an `error`. labnotes runs it once per run, from a fresh run folder, with each experiment's `command` from `experiments/<experiment>/experiment.toml`; those commands pass `--output .`.

```
uv run --project packages/gbnf_experiment run_gbnf_experiment --output /tmp/probe --source-language python --include-unit-tests 1 --include-source-integration-tests 1 --include-target-integration-tests 1
```

| Flag | What it is |
| --- | --- |
| `--output` | Required, no default. The run folder itself, created if missing; no id or subfolder is picked. |
| `--source-language` | `javascript` or `python`. The port goes to the other. |
| `--include-unit-tests` | `0` or `1`, default `0`. Include the source's unit tests, beside the modules they test. |
| `--include-source-integration-tests` | `0` or `1`, default `0`. Include the source's generated integration suite. |
| `--include-target-integration-tests` | `0` or `1`, default `0`. Include the target's generated integration suite. |
| `--model` | Passed to `ClaudeAgent`. Default `claude-opus-5`. |
| `--effort` | Passed to `ClaudeAgent`. Default `high`. |
| `--debug` | Show the prepare image's build output. |

Everything gbnf-specific lives here: the pin, the patches, the test generation, the rules. Grading the port against the held-out suite is a separate step and not part of a run.

A run that raises still writes `manifest.json` with the error, then re-raises.

Auth is `API_KEY` in `config.py`. Blank, the default, runs on the host's Claude subscription; the host's `ANTHROPIC_API_KEY` is never read. Set, the agent bills that key. Nothing is read from the environment.

Depends on port_codebase and botbox.
