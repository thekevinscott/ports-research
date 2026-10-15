# 2026-10-15T19:35Z — Afternoon runs billed the API key; first subscription-only batch launched

Kevin wanted to measure subscription cost per run. Two batches today ran on `ANTHROPIC_API_KEY` instead, against his instruction not to use the key. The subscription figures did not move, which is how it surfaced.

- 15:40Z batch (`matrix-20261015T154057Z.jsonl`): 9 runs, 6 exit 0, 3 exit 137. Stopped by SIGINT at ~15:55Z.
- 18:35Z batch (`matrix-20261015T183537Z.jsonl`): launched `-k 5`, SIGINT once five were in flight. 4 banked (opus low py 0, sonnet high js 0, fable high js 0, haiku max js 137); the fifth, opus max js, was killed mid-run at Kevin's "No!".
- Cause: both launches reused the `--env-file .env` command from the session handoff; the runner's default is `--auth api-key`, and the `auth api-key` startup line was not read as a problem. Kevin's instruction was not in the handoff.
- Kevin deleted `.env`. The runner's `--auth subscription` mode is now the only path.
- 19:27Z batch (`matrix-20261015T192727Z.jsonl`): `--auth subscription -k 5`, `ANTHROPIC_API_KEY` unset, startup line `auth subscription`. SIGINT once five were in flight. Baseline before: 51% weekly, 3% session. The after-reading is Kevin's.
- Every per-run subscription estimate made earlier today is void: none of the 397 runs in the last week touched the subscription.
