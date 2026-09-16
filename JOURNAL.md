# Journal

Lab notes for the porting experiment. Append-only. One entry per major event:
a run started or finished, a finding, a decision, a tool landed. UTC
timestamps. Newest at the bottom. Session handoffs under `internal/` carry
state between sessions; this file carries the record.

## 2026-09-16T22:23Z v2 kicked off

The v1 post is live at thekevinscott.com/can-an-agent-port-a-codebase/. v1 is
tagged on `f21cd76`. Kevin's v2 list, given today: whitelist instead of
blacklist for the agent's tree; the transcript viewer from
agent-transcript-viewer as part of v2; API coverage tests separate from the
integration tier; a timestamped journal; every change on a `.worktrees/`
branch pushed to a PR; deeper analysis on embeddings and AST; re-read the
literature survey; review Mistral's Fortran-to-C++ case study, in particular
the scaffold-first idea; run with other models.

Swept `internal/` for earlier asks not on today's list. Found three: unit vs
integration tests as separate conditions (2026-09-09), a fidelity scale
(2026-09-09), and larger n (2026-09-09, later ruled out of scope on
2026-09-10). Redo scope was left as Kevin's call on 2026-09-14; the whitelist
settles it as a full re-run, since any assembly change moves the corpus.

Plan written to `notes/PLAN_2026-09-16-v2.md` on branch `v2-plan`.

## 2026-09-16T22:41Z whitelist placement decided

Kevin: "the whitelist should be made generic, and there should be a way to
define it from gbnf-experiment". The copy-by-allow-set step and its tests go in
porting-harness, which today receives a finished tree and does no assembly.
gbnf-experiment supplies the set and drops its three removers. Plan updated.
