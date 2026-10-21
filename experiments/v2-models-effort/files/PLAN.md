# Model and effort study

Question: how do the model and its effort level change the port, with the test configuration fixed. The configuration is the one the test-configuration study pointed at as the defensible default. Kevin, 2026-10-12: "the only defensible position it seems is to ship source tests and hold out target tests."

## Design

The grid is in [experiment.toml](experiment.toml); each run is one `run_gbnf_experiment` call. Four models (Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5) at five effort levels (low, medium, high, xhigh, max), both source languages, unit tests plus source integration tests, no target integration tests. 40 cells, 12 completed runs per cell, 480 runs. Prompt: the 2026-10-15 rewrite (harness commit `3cc2947` or its rebased twin `11beb02`); runs from before it are marked `excluded` in their `run.json`. The test-configuration study ran on the earlier prompt.

A completed run is `run.json` `exit_code` 0 and not excluded. Failed runs (OAuth revocation, oomd kill, request timeout) are not counted and are rerun.

## Origin

Kevin, 2026-10-15: "Burn through this 5 hour chunk and the next one please" ... "follow it up with effort. Every effort level please". The four models at medium ran first (journal `2026-10-15T03-27Z`); the other four efforts were queued behind it (`2026-10-15T03-40Z`). The two became one script with one cell grid when the runner learned to skip completed cells (PRs #199, #200).

## Running

- Subscription only: `API_KEY` stays blank in `gbnf_experiment/config.py`. Kevin, 2026-10-15: "I specifically said NOT TO USE the api key!"
- `--concurrency 5`. Kevin, 2026-10-15: "Let's run it with 5 concurrent."
- Runs bank in `experiments/v2-models-effort/runs/<id>/`, tracked by DVC. Session logs from the old scheduler are in `data/sessions/`.

## Progress

Report completed and remaining against 12 per cell, then the per-cell table, all four models included:

```
uvx dirsql --no-ignore -c experiments/.dirsql.toml "SELECT model, effort, source_language, COUNT(*) AS n FROM runs WHERE experiment='v2-models-effort' AND exit_code=0 AND excluded IS NOT 1 GROUP BY model, effort, source_language"
```

Launches, stops and failures are journal entries under `journal/`, dated 2026-10-15 and later.
