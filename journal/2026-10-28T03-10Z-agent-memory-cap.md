# 2026-10-28T03:10Z Agent containers capped at 8g

run_gbnf_experiment takes `--memory`, default `8g`, and port_codebase passes it to Botbox (PR #250, on botbox 0.1.77 from PR #249). botbox sets `--memory` and `--memory-swap` to the same value, so the agent gets 8g and no swap. The v2-models-effort `command` now states `--memory 8g`.

Runs banked before this ran uncapped; runs from here on are capped. Recorded in `experiments/v2-models-effort/files/DEVIATIONS.md`. Decided by Kevin 2026-10-27 as part of the memory-cap plan (approved: "Yes").
