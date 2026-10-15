# 2026-10-15T02:14Z — Fable then Sonnet study launched

Kevin, 2026-10-14: "Kick off an experiment. Fable sub agents, source unit and source integration tests." Then: "keep the n, both directions. Do fable. If there's still tokens left over, do sonnet."

One test configuration: unit tests plus source integration tests, no target integration tests. Both directions, n=12, effort medium, k=6. Prompt byte-identical to V2.

- Harness: `.worktrees/botbox-bump` at 87066d8 (the V2 study commit), subscription auth.
- Cells: `source-python_unit-tests_source-integration-tests_effort-medium_model-<model>` and `source-javascript_...`.
- Sequence: claude-fable-5-1 first, then claude-sonnet-5-5 if the Fable cells exit 0. Script `/tmp/claude/study-2026-10-14/sequence.fish`, PID 2291155.
- Fable jsonl: `.worktrees/botbox-bump/data/runs/matrix-20261015T021426Z.jsonl`. Log `internal/study_2026-10-14-claude-fable-5-1.log`.
- Usage at launch: five_hour 3, seven_day 8.
