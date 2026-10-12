# Analysis plan: effect of test inclusion (2026-10-12)

The question for this cycle, in Kevin's words: "what effect does test inclusion have on produced output". The goal is a preliminary answer that is "relatively focused, a bit cheap", so that model comparison can start on one fixed test configuration. For libraries other than gbnf, Kevin's position: "the only defensible position it seems is to ship source tests and hold out target tests".

Checked boxes are merged. Open PRs are named.

## Data

- [x] Study design: 16 cells (2 source languages x 3 test flags: `include_unit_tests`, `include_source_integration_tests`, `include_target_integration_tests`), model claude-opus-5-5, effort medium, 12 runs per cell (PR #117).
- [x] Resume, batch cap, fail-fast on billing or auth errors (PR #120).
- [ ] All 192 runs with exit 0 banked (study 1: 119; study 2 in progress).
- [ ] Run directories and matrix jsonl files in the main checkout's `data/runs/`.
- [ ] Exclusion rule written down: non-zero exit (api_error, exit 137) excluded from every forward table, counted in a sidebar.

## Measures

One row per run, one column per measure, all in the runs notebook ([analysis/notebook](../analysis/notebook/README.md)).

### Already in the notebook

- [ ] Run table reads the V2 manifest schema (three flags, javascript target, exit code) and labels V2 rows by flags and source language (PR in flight).
- [ ] Cost: total tokens, API calls, wall time.
- [ ] Size: file count, LOC.
- [ ] Test pass rates: target integration pass rate is a fair measure only in the 8 cells where the target suite was not shipped; the table says so.
- [ ] Reference diff: similarity, kept, identical, modified, renamed, added, deleted.
- [ ] Levenshtein: token, character, path.
- [ ] Embeddings: embedding-server pass over every V2 run so the per-run cache exists.
- [ ] AST: parked. Kevin, 2026-10-12: "AST I find interesting but our initial attempt I didn't really understand and it seemed to say very little." The plain-language explainer asked for on 2026-09-10 is still owed.

### Held-out behavior

- [x] Package: [analysis/measure-behavior](../measure-behavior/README.md), 100 generated grammars, 799 inputs, seed 0, never mounted into any agent container; accept, reject, error, crash per pair; agreement rate and confusion table (PR #118).
- [ ] Notebook section: `behavior_agreement_pct` lead, confusion counts in the accordion, dots per run with median ticks, one panel per source language (PR in flight).

### Held-out API

- [ ] Delete `analysis/exercise-api` (PR in flight). Kevin: "drop exercise api and start fresh with that".
- [ ] Package `analysis/measure-api`: seeded corpus, per-step rule-set comparison against the reference, outcomes match, mismatch, error_match, error_mismatch, crash; agreement rate and confusion table (PR in flight).
- [ ] Notebook section, same shape as the behavior section.

### Transcripts, mechanical

- [ ] A parser from transcript jsonl to per-run columns. What the agent read (source, shipped tests, both, neither); how often it ran which suite and the pass counts it saw; whether it wrote its own tests or a differential script against the reference; Bash calls, turns, tokens per phase.
- [ ] Notebook section, charted by test inclusion.

### LLM judges

Kevin, 2026-10-12: "we should run the judge suite against the base ports without telling them, so we can measure a baseline of what they say by default." The base ports are the two hand-written gbnf implementations judged against each other, in both directions. They enter the suite as ordinary items; the judge is never told which items are agent ports and which are the human pair.

- [ ] Code judge rubric, written before any V2 port is read: API parity, structure kept or changed and why, semantic divergences with quoted lines, idiom versus transliteration. Output per item: a verdict per rubric line with quoted evidence, plus one ordinal fidelity score.
- [ ] Transcript judge rubric, written before any V2 transcript is read: did the agent cheat; why did it keep or change the file structure (the two open questions from the [V2 plan](PLAN_2026-09-16-v2.md)). Input is the compressed transcript: commands and assistant text, tool output dropped.
- [ ] Baseline: the human pair, both directions, judged blind. Its scores are the default reading of the code judge for a faithful port.
- [ ] One pass over every exit-0 run with a stronger model than the one under test, uncertain items escalated to Kevin. Each item judged once; the judge sees items in shuffled order.
- [ ] Notebook section: fidelity score and verdict counts by test inclusion, with the human pair drawn as a reference line.

### Not this cycle

- Fidelity scale, internal-state parity script (Mistral), grader validation by mutation.
- Literature only: property-based and metamorphic relations, differential symbolic execution, doc-as-spec judging, security gate. See [literature/SYNTHESIS.md](../literature/SYNTHESIS.md).

## Statistics

Kevin, 2026-09-16: "You are fully in charge of statistics." The proposal, unchanged from the V2 plan:

- [ ] Per flag, compare the 96 runs with it on to the 96 with it off, within source language and pooled.
- [ ] Permutation test on the difference in medians; bootstrap interval on the gap; minimum detectable gap stated up front, so a null reads as "too small to see", never "no effect".
- [ ] Charts: per-run dots with median ticks. No mean bars.

## Decision

- [ ] Fix the forward configuration as source unit and source integration tests in, target integration tests out.
- [ ] Check it is not clearly worse than no tests on held-out behavior and API agreement.
- [ ] Report the target-tests-in cells as a ceiling, not a candidate.
- [ ] Write the preliminary conclusion as a journal entry and start the model comparison.
