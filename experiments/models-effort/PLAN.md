# Model and effort study

Question: how do the model and its effort level change the port, with the test configuration fixed. The configuration is the one the test-configuration study pointed at as the defensible default. Kevin, 2026-10-12: "the only defensible position it seems is to ship source tests and hold out target tests."

## Design

The grid is in [design.yaml](design.yaml); the script that runs it is `packages/gbnf_experiment/scripts/study_model_effort.py`. Four models (Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5) at five effort levels (low, medium, high, xhigh, max), both source languages, unit tests plus source integration tests, no target integration tests. 40 cells, 12 completed runs per cell, 480 runs. Prompt: the 2026-10-15 rewrite (`prompt_since: 3cc2947` in design.yaml); the test-configuration study ran on the earlier prompt.

A completed run is exit code 0 with no error and a completion time. Failed runs (OAuth revocation, oomd kill, request timeout) are not counted and are rerun. The runner counts banked completed runs per cell at startup and skips cells that already have 12.

## Origin

Kevin, 2026-10-15: "Burn through this 5 hour chunk and the next one please" ... "follow it up with effort. Every effort level please". The four models at medium ran first (journal `2026-10-15T03-27Z`); the other four efforts were queued behind it (`2026-10-15T03-40Z`). The two became one script with one cell grid when the runner learned to skip completed cells (PRs #199, #200).

## Running

- `--auth subscription` only. Kevin, 2026-10-15: "I specifically said NOT TO USE the api key!"
- `--concurrency 5`. Kevin, 2026-10-15: "Let's run it with 5 concurrent."
- Fable is off while it times out silently (removed from `MODELS` as a local edit in the running worktree, not committed). Its cells stay in the design and in the progress table.
- Each launch appends to its own `data/runs/matrix-<ts>.jsonl`; completed runs bank in `data/runs/<ts>_<id>/`, tracked by DVC.

## Progress

Report completed and remaining against 12 per cell, then the per-cell table, all four models included:

```
uvx dirsql --no-ignore -c data/.dirsql.toml "SELECT model, effort, source_language, COUNT(*) AS n FROM runs WHERE study='v2-model-effort' AND exit_code=0 GROUP BY model, effort, source_language"
```

Launches, stops and failures are journal entries under `journal/`, dated 2026-10-15 and later.
