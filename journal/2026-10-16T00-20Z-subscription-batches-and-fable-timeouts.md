# 2026-10-16T00:20Z — Two subscription batches of the model-effort study; Fable xhigh/max requests time out

Both batches ran `study_model_effort.py --auth subscription` from the root `data/runs`, skipping completed cells via dirsql. Numbers are from `result.json` and the batch jsonl; nothing here reads the ports.

## Batch 1: 19:27Z, k=5, SIGINT after 5 submissions

| cell | exit | minutes |
|---|---|---|
| sonnet low, js | 0 | 2 |
| haiku high, py | 0 | 13 |
| haiku high, js | 0 | 17 |
| opus max, js | 137 | 40 |
| sonnet max, js | 0 | 147 |

Weekly subscription reading: 51% before, 53% after. Session reading reset mid-batch, so only weekly is usable.

## Batch 2: 21:57Z, k=3, `--runs 9`

| cell | exit | minutes | turns | output tokens |
|---|---|---|---|---|
| haiku medium, js | 0 | 7 | 57 | 95k |
| haiku low, js | 0 | 9 | 51 | 109k |
| opus high, js | 0 | 9 | 32 | 70k |
| fable low, py | 0 | 14 | 35 | 66k |
| opus xhigh, py | 0 | 28 | 65 | 150k |
| sonnet xhigh, js | 0 | 35 | 80 | 164k |
| haiku high, js | 137 | 19 | | |
| fable max, js | 1 | 64 | 28 | 9.7k |
| fable xhigh, py | 1 | 60 | 21 | 20k |

Session reading: 3% at launch, 36% at 00:15Z, with chat in the same window. Weekly not yet read.

## Findings

- **Exit 137 at k=3 is still systemd-oomd.** haiku high js was killed at 23:05:51Z with the host at 47.0 GB. Concurrency 3 lowers the odds; it is not a bound.
- **Both Fable cells above `high` ended with `Request timed out`**, `is_error: true`, exit 1, each after about an hour wall clock and under 30 turns. The runner classes the message as a credit/auth failure and stops submitting. Whether the timeout is in Claude Code, the harness, or the API is not established. The completed-run predicate excludes both.
- Model-effort totals after banking: 149 banked, 121 exit 0, of 480 cells. `dvc push` sent 541 files.
