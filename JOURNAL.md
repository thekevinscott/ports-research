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

## 2026-09-16T22:47Z plan reorganized into three sections

Kevin: "4 does not belong in prepatory work. So there's 3 sections - prepatory,
running, analysis", and "Let's number starting from 1 in each section". Agents
and models moved under Running next to the re-run. Post-run work is now
Analysis.

## 2026-09-16T22:48Z literature review moved to the end

Kevin: "Literature review - I think that should come after v2. Right? I don't
want to bias myself; and I don't wanna go too deep too early". It is now the
last Analysis item, after the v2 results.

## 2026-09-16T22:48Z fourth section for outside reading

Kevin: "same with mistral. So maybe it's _four_ sections". Mistral review and
literature review now sit in an After v2 section, numbered from 1.

## 2026-09-16T22:50Z fidelity scale deferred to v3

Kevin: "A better understanding of what faithful means - totally want to dig in
on this. this feels like a v3 thing though. My hope is that the initial
experiment reveals some directions in which to go."

## 2026-09-16T22:51Z check-in oracle idea parked

Kevin proposed an in-loop oracle: a stronger model the agent can ask whether an
action is "kosher", escalating to a human when unsure. He parked it as out of
scope for v2. Recorded under earlier asks so it is not lost.

## 2026-09-16T22:54Z post-hoc judge adopted

The check-in oracle becomes a post-hoc judge: a stronger model scores every
banked transcript against a fixed cheating rubric and escalates uncertain runs
to Kevin. Kevin: "I love your counter proposal on my check-in! Yes absolutely."
Added under Analysis, transcript questions.

## 2026-09-16T22:59Z review of experiment strength: two adopted, three declined

Two agents reviewed the repo docs, the post and its four linked sources. Kevin
adopted a written protocol (pinned harness, clean tree, shuffled cell order,
exclusion rule, fixed before run one) and grader validation by mutation, both
recorded in the plan as agent-initiated with his approval. He declined holding
the graded suite out of the mount, the human-port baseline, and a
"report how" transcript item.

## 2026-09-16T23:11Z thinking redaction is transport, not model

Re-counted thinking blocks over 103,338 local Claude Code transcripts. opus-5
via the first-party API: 0 of 8,931 with text. Claude Code pointed at
openrouter, same model: 16 of 16 with text. The gate on thinking text is
dropped from the plan; pi via openrouter is expected to bank it. Kevin also put
the agent in charge of statistics; a Statistics section is added under
Analysis. exercise-api goes to v3, Kevin leaning to start fresh.
