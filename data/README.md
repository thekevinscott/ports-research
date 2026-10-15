# data

`runs/<UTC timestamp>_<token>/` is one run: `manifest.json` (the condition, the study, exit code, error), `result.json` (the agent CLI's final JSON), `stderr.txt`, `transcript/`, `proxy.log`, `ported_implementation/`. `runs/matrix-<timestamp>.jsonl` is one study launch, one line per run. `judge/` and `walkthroughs/` are notebook outputs and have no tables here.

## Querying with dirsql

`.dirsql.toml` declares three tables over `runs/`. dirsql loads it only when told to (`-c`); the globs resolve against this directory, so the command works from anywhere. From the repo root:

```
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT study, COUNT(*) FROM runs GROUP BY study"
```

`--no-ignore` is required: `runs/`, `judge/` and `walkthroughs/` are DVC-tracked and listed in `data/.gitignore`, which dirsql honors by default. `uv tool install dirsql` makes it `dirsql --no-ignore -c ...`. `jq` must be on PATH: each table's rows come from a `jq` hook over the matched files.

| Table | One row per | Columns |
| --- | --- | --- |
| `runs` | `runs/*/manifest.json` | `run_id`, `study`, `timestamp`, `completed_at`, `exit_code`, `error`, the condition (`name`, `source_language`, `target_language`, `model`, `effort`, the `include_*` flags; V1 rows fill `include_python_tests`/`include_typescript_tests`, V2 rows the other three), `harness_commit` |
| `results` | `runs/*/result.json` | `run_id`, `is_error`, `terminal_reason`, `stop_reason`, `num_turns`, `duration_ms`, `result_index`, and `usage`'s `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` |
| `matrix` | line of `runs/matrix-*.jsonl` | `log`, `run_id`, `round`, `exit_code`, `error`, `wall_seconds`, `started_at`, `finished_at`, the cell (`source_language`, `model`, `effort`, the three `include_*` flags) |

Examples:

```
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT study, exit_code, COUNT(*) FROM runs GROUP BY 1, 2 ORDER BY 1, 2"
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT run_id, model, effort, terminal_reason FROM runs JOIN results USING (run_id) WHERE is_error = 1"
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT log, COUNT(*), SUM(exit_code = 0) FROM matrix GROUP BY log"
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT run_id FROM runs WHERE completed_at IS NULL"
```

With no query, the same command opens a REPL. Output is a table on a terminal and JSON when piped; `--format table` or `--format json` forces one.
