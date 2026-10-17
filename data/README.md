# data

`runs/<experiment>/<run>/` is one run: `run.json` (labnotes' record: `params`, `created`, `ended`, `exit_code`, and `excluded`/`reason` for runs from before the experiment's prompt), `manifest.json` (the condition, the container's exit code, error), `result.json` (the agent CLI's final JSON; absent when the run never finished), `stderr.txt`, `transcript/`, `proxy.log`, `ported_implementation/`. `sessions/matrix-<timestamp>.jsonl` is one old study launch's log. `orphans/` holds run folders with no manifest. `judge/` and `walkthroughs/` are notebook outputs.

## Querying with dirsql

`.dirsql.toml` declares one table, `runs`. dirsql loads it only when told to (`-c`); the glob resolves against this directory, so the command works from anywhere. From the repo root:

```
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT experiment, COUNT(*) FROM runs GROUP BY experiment"
```

`--no-ignore` is required: `runs/` is DVC-tracked and gitignored, and dirsql skips gitignored files by default. `uv tool install dirsql` makes it `dirsql --no-ignore -c ...`. `jq` must be on PATH: the rows come from one `jq` call over every `run.json`, `manifest.json` and `result.json`.

`runs`: one row per run directory, `run.json`, the manifest and `result.json` merged.

| From | Columns |
| --- | --- |
| directory names | `run_id`, `experiment` |
| run.json | `exit_code`, `excluded`, `reason`, `created`, `ended` |
| manifest | `timestamp`, `completed_at`, `container_exit_code` (the manifest's `exit_code`), `error`, `harness_commit`, `harness_dirty`, `sandbox_image_id`, `gbnf_commit`, `reference_files` (JSON list) |
| manifest `condition` | `name`, `source_language`, `target_language`, `model`, `effort`, `include_unit_tests`, `include_source_integration_tests`, `include_target_integration_tests` (V2), `include_python_tests`, `include_typescript_tests` (V1) |
| result.json | `is_error`, `terminal_reason`, `stop_reason`, `subtype`, `api_error`, `api_error_status`, `num_turns`, `queued_turn_count`, `result_index`, `safety_stops`, `duration_ms`, `duration_api_ms`, `ttft_ms`, `ttft_stream_ms`, `time_to_request_ms`, `first_content_frame_ms`, `fast_mode_state`, `fast_mode_disabled_reason`, `session_id`, `uuid`, `result`; nested objects as JSON text: `usage`, `model_usage`, `subagent_stats`, `permission_denials`, `origin` |
| result.json `usage` | `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `thinking_tokens`, `speed`, `service_tier`, `inference_geo` |

Runs without a `result.json` have NULL in every result column. `total_cost_usd` is not a column.

Examples:

```
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT experiment, excluded, exit_code, COUNT(*) FROM runs GROUP BY 1, 2, 3 ORDER BY 1, 2, 3"
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT run_id, model, effort, terminal_reason FROM runs WHERE is_error = 1"
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT run_id FROM runs WHERE completed_at IS NULL"
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT model, effort, AVG(output_tokens) FROM runs WHERE experiment = 'models-effort' GROUP BY 1, 2"
```

With no query, the same command opens a REPL. Output is a table on a terminal and JSON when piped; `--format table` or `--format json` forces one.
