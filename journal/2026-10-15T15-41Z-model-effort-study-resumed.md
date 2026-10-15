# 2026-10-15T15:41Z — Model-effort study resumed, skipping banked runs

`study_model_effort.py` relaunched at Kevin's "Let's run it with 5 concurrent", the first run since "Do not run any more experiments" this morning. #199 made the runner count the study's completed runs under `--output` through dirsql and skip cells that already have `--n`; `--resume` is gone.

- Command: `uv run --env-file .env python scripts/study_model_effort.py --output data/runs -k 5`, from `.worktrees/fix-study-model-effort` (PR #200 restores the script after #199 left the wrong version in main; the fix is the script's pre-#199 text, so the run is the same code either way).
- Startup shortfall: 384 of 480. Skipped: 102 completed runs over 10 cells (fable/haiku/opus/sonnet medium, fable low, haiku low). The 19 failed runs are not counted.
- Log: `data/runs/matrix-20261015T154057Z.jsonl`; stdout/stderr in `/tmp/claude/study-model-effort-20261015.log`.
