# 2026-10-16T00:50Z — The Fable timeouts: ten five-minute attempts with no response bytes

Corrects the open question in `2026-10-16T00-20Z-subscription-batches-and-fable-timeouts.md`.

Both failed Fable runs (`20261015T220413Z_11b5d0aa` max js, `20261015T224413Z_e9250a19` xhigh py) show the same shape in the transcript and `proxy.log`:

- After a normal tool result, Claude Code opened a request to `api.anthropic.com`. The proxy shows the connection established, then closed by the client 300 s later with no bytes read. Claude Code logs `Request timed out.`, `retryAttempt` 1 of 9.
- Nine more attempts, each exactly 300 s, with backoff up to 40 s between them. The final `isApiErrorMessage` row is "Request timed out". Ten attempts plus backoff is the ~60 min wall clock.
- Context at the hung request: ~118k and ~122k tokens. The preceding assistant turns were ordinary (878 and 15.6k thinking tokens).

The same shape appears in the morning Fable max js run (`20261015T080534Z_4cdb190e`, API key): three 300 s timeouts, then the spend-limit error ended it. That run also contains a single successful response that took 1305 s, so long responses do complete; the failing requests sent nothing at all for five minutes, ten times running.

Fable was serving during the window: fable low py (`20261015T223302Z_dd519b23`) received 67 responses between 22:33Z and 22:46Z, and the xhigh run itself received 37 before its hang.

Counts across the 149 banked model-effort runs: Fable above `high`, 3 runs, 3 with the timeout pattern. Fable at `high` or below, 37 runs, 0. Other models at any effort, 109 runs, 0 (one run each at opus max and sonnet max completed single responses of 698 s and 426 s).

The 300 s per attempt and 9 retries are Claude Code's client settings; which setting is not confirmed. Whether the API was computing or stalled on those requests is not observable from this side.
