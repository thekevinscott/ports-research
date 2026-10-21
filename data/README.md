# data

`experiments/<experiment>/runs/<run>/` is one run: `run.json` (labnotes' record: `params`, `created`, `ended`, `exit_code`, and `excluded`/`reason` for runs from before the experiment's prompt), `manifest.json` (the condition, the container's exit code, error), `result.json` (the agent CLI's final JSON; absent when the run never finished), `stderr.txt`, `transcript/`, `proxy.log`, `ported_implementation/`. `sessions/matrix-<timestamp>.jsonl` is one old study launch's log. `orphans/` holds run folders with no manifest. `judge/` and `walkthroughs/` are notebook outputs.

## Querying with dirsql

See [experiments/README.md](../experiments/README.md).
