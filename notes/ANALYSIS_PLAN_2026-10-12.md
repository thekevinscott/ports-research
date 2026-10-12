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

- [x] Run table reads the V2 manifest schema (three flags, javascript target, exit code) and labels V2 rows by flags and source language (PR #124).
- [ ] Cost: total tokens, API calls, wall time.
- [ ] Size: file count, LOC.
- [ ] Test pass rates: target integration pass rate is a fair measure only in the 8 cells where the target suite was not shipped; the table says so.
- [ ] Reference diff: similarity, kept, identical, modified, renamed, added, deleted.
- [ ] Levenshtein: token, character, path.
- [ ] Embeddings: embedding-server pass over every V2 run so the per-run cache exists.
- [x] AST, relative to the reference. Kevin, 2026-10-12: "AST I find interesting but our initial attempt I didn't really understand and it seemed to say very little." and "AST in particular I think we could go deeper". Today's seven measures describe the port alone. Each becomes relative:
  - [x] Delta to the human port: measure-ast on the hand-written target-language implementation once; every measure shown as port minus reference (PR #129).
  - [x] Function-level matching: port functions paired with reference functions by normalised name and arity; matched fraction, unmatched on each side, line-count drift per pair (PR #129).
  - [x] Tree edit distance on matched pairs, identifiers abstracted (GumTree style) (PR #129).
  - [x] Branch structure: distance between the per-function cyclomatic distributions of port and reference (PR #129).
  - [x] Public API surface: exported names and signatures, port versus reference, as a set diff (PR #129).
  - [x] All labelled structural drift, never fidelity alone: CodeBLEU's AST and dataflow subscores do not track functional correctness in the papers the embeddings review covers (PR #129, PR #133).
  - [x] Notebook section: `ast_matched_fraction`, `ast_tree_edit_median` and `ast_branching_wasserstein` leads, the other AST columns in the accordion, dots per run with median ticks, one panel per source language; the leads join the V2 statistics (PR #133).
  - [x] The plain-language explainer asked for on 2026-09-10: one generated sentence per public entry point, per run, in the notebook's call-path accordion (PR #142, PR #146).
  - [x] Call-path fidelity, after Sean Goedecke's [How to read code](https://www.seangoedecke.com/how-to-read-code/), which Kevin sent on 2026-10-12: "The canonical way to read code might be an additional clue for how to measure fidelity". Start at each shared public entry point, follow call expressions within the package with callees resolved by the normalised name and arity already used for pairing, everything outside the package a black box. Per entry point: edit distance between the reference's and the port's callee sequences, and the share of reference call edges present in the port. A function unreachable from the public API weighs nothing. A `measure-ast` extension with its own notebook columns; its per-entry-point output ("the port skips the error path after step four") is the explainer above. Done: `call_paths` in `measure-ast compare` (PR #142); `ast_mean_edge_recall` and `ast_median_trace_normalised` leads, reachability columns and the per-run explainer table in the notebook (PR #146).

### Held-out behavior

- [x] Package: [analysis/measure-behavior](../measure-behavior/README.md), 100 generated grammars, 799 inputs, seed 0, never mounted into any agent container; accept, reject, error, crash per pair; agreement rate and confusion table (PR #118).
- [x] Notebook section: `behavior_agreement_pct` lead, confusion counts in the accordion, dots per run with median ticks, one panel per source language (PR #127).

### Held-out API

- [x] Delete `analysis/exercise-api` (PR #123). Kevin: "drop exercise api and start fresh with that".
- [x] Package `analysis/measure-api`: seeded corpus, per-step rule-set comparison against the reference, outcomes match, mismatch, error_match, error_mismatch, crash; agreement rate and confusion table (PR #126).
- [x] Notebook section, same shape as the behavior section (PR #131).

### Transcripts, mechanical

- [x] A parser from transcript jsonl to per-run columns. What the agent read (source, shipped tests, both, neither); how often it ran which suite and the pass counts it saw; whether it wrote its own tests or a differential script against the reference; Bash calls, turns, tokens per phase. (PR #134)
- [x] Notebook section, charted by test inclusion (PR #135).
- [ ] Reading order, after the same article: whether the first file read is a public entry point, files read before the first write, re-reads of the same file, search calls per file read. Mechanical, from the transcript jsonl.

### LLM judges

Kevin, 2026-10-12: "we should run the judge suite against the base ports without telling them, so we can measure a baseline of what they say by default." The base ports are the two hand-written gbnf implementations judged against each other, in both directions. They enter the suite as ordinary items; the judge is never told which items are agent ports and which are the human pair.

- [x] Code judge rubric, written before any V2 port is read: API parity, structure kept or changed and why, semantic divergences with quoted lines, idiom versus transliteration. Output per item: a verdict per rubric line with quoted evidence, plus one ordinal fidelity score (PR #132).
- [x] Transcript judge rubric, written before any V2 transcript is read: did the agent cheat; why did it keep or change the file structure (the two open questions from the [V2 plan](PLAN_2026-09-16-v2.md)). Input is the compressed transcript: commands and assistant text, tool output dropped (PR #132).
- [x] Baseline: the human pair, both directions, judged blind. Its scores are the default reading of the code judge for a faithful port (PR #132).
- [ ] One pass over every exit-0 run with the same model family at higher effort, uncertain items escalated to Kevin. Each item judged once; the judge sees items in shuffled order. Both rubrics, in progress since 2026-10-12 12:25Z at four concurrent calls each. Kevin, 2026-10-12, once every run was banked: "perhaps let's re prioritize both sets of judges" and "we have plenty left. We should exhaust this five hour block and the next one too please".
- [x] Transcript rubric item `reading_strategy`: entry-point-traced, directory-order, tests-first, mixed, unclear; the first reads quoted in order as evidence. Landed before the transcript pass (PR #139).
- [x] Code rubric: the judge traces the happy path from each public entry point through both implementations and quotes the first divergence as evidence for `semantic_divergences` (PR #139).
- [ ] Notebook section: fidelity score and verdict counts by test inclusion, with the human pair drawn as a reference line.

### Derived walkthroughs

Kevin, 2026-10-12: "In particular I wonder about asking an LLM to write explainers or walk through of the code- then compare those derivations". Each implementation is explained on its own, so the explainer never sees the other side, and both explanations are English, so the language difference drops out.

- [ ] Fixed walkthrough format, following the article's method: for each public entry point, the happy path as ordered one-sentence steps naming what happens and what is called; then error paths; then invariants. Structured JSON.
- [ ] One walkthrough per reference per language and one per port, each from one implementation alone, cached by content. Subscription billing, same model family as the judge.
- [ ] Mechanical comparison: align port steps to reference steps by embedding similarity with the embedding server; per entry point, coverage (share of reference steps matched), order agreement, extra steps. A short LLM comparison of aligned pairs only if the embeddings prove too coarse.
- [ ] Two reference lines, both free of ports: the noise floor (the same reference explained twice and compared) and the baseline (the python and javascript references explained independently and compared).
- [ ] Notebook section: coverage lead with the noise floor and baseline drawn as lines, per-entry-point table of missing and extra steps.

### Not this cycle

- Fidelity scale, internal-state parity script (Mistral), grader validation by mutation.
- Literature only: property-based and metamorphic relations, differential symbolic execution, doc-as-spec judging, security gate. See [literature/SYNTHESIS.md](../literature/SYNTHESIS.md).

## Statistics

Kevin, 2026-09-16: "You are fully in charge of statistics." The proposal, unchanged from the V2 plan, plus the basics the notebook lacks today:

- [x] n per cell, visible on every chart and in a summary table; exclusions counted beside it (PR #130).
- [x] Interquartile range beside every median (PR #130).
- [x] Failures by cell (exit 137, api_error) and cost per successful run, in a sidebar table (PR #130).
- [x] Spearman correlation matrix of every per-run measure against held-out behavior and API agreement, so the cheap proxies are validated on our own data (PR #130, PR #131).
- [x] The "How to read" text rewritten for V2 (PR #130).

- [x] Per flag, compare the 96 runs with it on to the 96 with it off, within source language and pooled (PR #130).
- [x] Permutation test on the difference in medians; bootstrap interval on the gap; minimum detectable gap stated up front, so a null reads as "too small to see", never "no effect" (PR #130).
- [x] Charts: per-run dots with median ticks. No mean bars (PR #127, PR #130).

## Decision

- [ ] Fix the forward configuration as source unit and source integration tests in, target integration tests out.
- [ ] Check it is not clearly worse than no tests on held-out behavior and API agreement.
- [ ] Report the target-tests-in cells as a ceiling, not a candidate.
- [ ] Write the preliminary conclusion as a journal entry and start the model comparison.
