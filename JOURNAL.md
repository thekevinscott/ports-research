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

## 2026-09-16T22:27Z whitelist placement decided

Kevin: "the whitelist should be made generic, and there should be a way to
define it from gbnf-experiment". The copy-by-allow-set step and its tests go in
porting-harness, which today receives a finished tree and does no assembly.
gbnf-experiment supplies the set and drops its three removers. Plan updated.

## 2026-09-16T22:29Z five decisions on the plan

Kevin, reviewing the plan in flight. The prompt gets updated ("we'll want to
update the prompt too"). Empty thinking text is on the fix list ("add this to
the list of things to fix"); the lever is model choice, since opus-5 through the
CLI writes none and fable does. API coverage tests are over gbnf's public
surface, and the goal is to delete execute-test-suite's adapters ("I want to be
able to remove the shim"). The plan cites the viewer's GitHub repo, not a local
path, because the plan is public. He asked what the derivation key was; it is
agent-proposed with no Kevin quote in the record, so writing it into the
manifest moves to Declined.

## 2026-09-16T22:31Z plan restructured into preparatory and post-run

Kevin: "Let's separate into prepatory work and post-run work", and "pi will be
done with openrouter, codex with openai, and claude with its denizens".
Preparatory: whitelist, prompt, API tier and shim removal, three agents on
three providers with a pilot each, viewer MVP. Then the re-run, 40 cells per
agent. Post-run: the transcript questions, the analysis learning track, the
Mistral review feeding a v3 scaffold decision.

## 2026-09-16T22:40Z derivation key dropped from the plan

Kevin: "let's get rid of derivation key". The Declined paragraph explaining it
is removed; the plan no longer mentions it.
