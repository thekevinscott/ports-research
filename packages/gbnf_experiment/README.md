# gbnf_experiment

Configures port_codebase for one library: [gbnf](https://github.com/thekevinscott/gbnf), which has javascript and python implementations sharing one test suite.

CLI `run_gbnf_experiment`. Each invocation is one experimental condition: a source language, and whether each language's test suite is mounted alongside the reference. It

- builds the prepare image in `docker/`, which clones gbnf at the pinned commit, applies `patches/`, and generates the test suites;
- selects the reference files for the condition into one source directory;
- hands that directory, a prompt and a `ClaudeAgent` to `port_codebase`;
- banks the `RunResult` as one run directory under `data/`: `manifest.json`, `result.json` (the agent CLI's stdout), `transcript/` (the transcript files, at their paths relative to the agent's home), `proxy.log`.

The prompt describes the source directory's layout, the target language, the package manager, and which suites are present. Paths in it are relative to the source directory.

```
uv run run_gbnf_experiment --source-language python --include-python-tests --include-javascript-tests
```

| Flag                        | What it is                                              |
| --------------------------- | ------------------------------------------------------- |
| `--source-language`         | `javascript` or `python`. The port goes to the other.    |
| `--include-javascript-tests` | Mount javascript's suite alongside the reference.       |
| `--include-python-tests`    | Mount python's suite alongside the reference.           |
| `--model`                   | Passed to `ClaudeAgent`. Default `claude-opus-5`.       |
| `--effort`                  | Passed to `ClaudeAgent`. Default `high`.                |
| `--debug`                   | Show the prepare image's build output.                  |

Everything gbnf-specific lives here: the pin, the patches, the test generation, the file selection. Grading the port against the held-out suite is a separate step and not part of a run.

A run that raises still writes `manifest.json` with the error, then re-raises.

Depends on port_codebase and botbox.
