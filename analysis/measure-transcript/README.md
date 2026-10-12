# measure-transcript

Mechanical per-run measures from a V2 run's Claude Code transcript: tool counts, reads, suite runs, own tests, differential scripts, fetch attempts, tokens. No judgments.

## Usage

```
measure-transcript --run <run dir>
```

Reads `<run>/manifest.json` (`condition.source_language`) and every `*.jsonl` under `<run>/transcript/`, subagent transcripts included, merged by timestamp. Prints one JSON object to stdout. Exits non-zero with a message when the run has no transcript or its source language is not `python` or `javascript`.

V2 layout only: the reference at `/input/python` and `/input/javascript`, the port at `/target`.

## Paths

Each path a call names is resolved against the cwd recorded with the call, following `cd` within a Bash command, and classed:

- `source_tests`, `target_tests`: under the source or the target language's shipped suite. python: `/input/python/tests/` and colocated `*_test.py`. javascript: `/input/javascript/integration-tests/` and colocated `*.test.ts`.
- `source`: any other path under the source language's directory.
- `port`: under `/target`.
- `other`: anything else.

Copies are followed. A `cp` maps its destination back to its origin, so a path inside a copied suite is that suite. A file the agent writes whole (Write tool, `>`/`>>` redirect, `tee`) is its own again; an Edit leaves a copy's class alone.

## Fields

- `turns`: assistant messages, counted by distinct message id.
- `bash_calls`, `read_calls`, `write_calls`, `edit_calls`: calls of each tool. `search_calls`: Glob and Grep calls.
- `read_source`, `read_source_tests`, `read_target_tests`: per call, one per class among the paths read. Reads are Read calls and `cat`, `head`, `less`, `grep`, `sed -n` in Bash; grep's pattern and sed's script are not paths.
- `touched_source_tests`, `touched_target_tests`: whether any Read, Write, Edit, Glob or Grep path, Bash argument, or suite run reached the class.
- `suite_runs`: per suite run, `turn`, `command` (the segment's words joined by spaces), `suite`, `passed`, `failed`. A suite run is pytest (also `python -m pytest`), vitest, jest, `node --test`, `npm`/`pnpm test` or `run test*`, or `just test*`, after env assignments, `timeout`, `time`, `uv run`, `npx` or `pnpm exec`.
  - `suite`: `source_tests`, `target_tests`, `own_tests`, or `unknown` when the run's paths (the cwd when none are given) reach more than one. A directory reaches every shipped suite under it or copied into it, and the agent's own tests when its written test files are under it. A path the reference reaches nowhere is the agent's own.
  - `passed`, `failed`: from the pytest, vitest, jest or node summaries in the call's output, paired with the command's suite runs in order only when their numbers match; else null.
- `suite_run_count`: length of `suite_runs`.
- `last_suite_counts`: per class, the last `{passed, failed}` with counts.
- `own_tests_written`, `own_test_files`: test files the agent wrote under `/target` and did not copy from `/input`, in order of first write. A test file is `test_*.py`, `*_test.py`, `*.test.*`, `*.spec.*`, or code under `tests`, `test`, `__tests__` or `integration-tests`.
- `differential_script`, `differential_evidence`: the first Bash command or Write whose script runs both runtimes, or names both a source path and a port path. A command runs a runtime when a segment's program is `python*`, `node`, `npx` or `tsx` (version checks aside) or a heredoc or `-c`/`-e` script names one as a string, at a line start or in a shebang. Evidence is `{turn, command}` or `{turn, path}`; null when none.
- `fetch_attempts`, `fetch_commands`: WebFetch and WebSearch calls, and `curl`, `wget`, `pip install` (also `pip3`, `python -m pip`, `uv pip`) and `npm install`/`npm i` segments, as `{turn, command}`.
- `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_creation_tokens`: summed over turns, each turn's usage counted once.
- `first_write_turn`: the first turn that writes under `/target` by Write, Edit, redirect or `tee`; null without one.
- `tokens_before_first_write`, `tokens_after_first_write`: input plus cache creation plus cache read plus output, summed over the turns before it and from it on; null without a write.
- `last_suite_run_turn`: turn of the last suite run; null without one.
