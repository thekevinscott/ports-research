# Methodology review, 2026-10-12

Kevin, 2026-10-12: "you should approach these results critically. Test it like an academic reviewer. Assume there are issues with methodology and critique harshly. Then fix. What you assume above- that's the right approach"; "Assume you are arguing with your professor. Or a reviewing board".

Kevin, 2026-10-12, on scope: "You should be critical of methodology but not of results (unless you're suspicious the results imply faulty methodology). I want to review the results together and draw conclusions together. I don't want to have to question the core methodologies though".

Scope: the V2 test-configuration study (2 source languages × 8 test-flag combinations, `claude-opus-5-5` at medium effort, 12 exit-0 runs per cell, 192 runs). This review covers the measures, detectors, judges, caches, statistics and exclusions. It does not cover results. Any number from the data is quoted only as evidence that a method is broken. Code is cited by repo path at main `bf020a2`. Fixes are listed per objection with their PR and merge commit.

## Summary

1. **Held-out behavior and API are coupled to the target flag through interface and layout.** Their drivers need the human target port's import path and names, which only the target integration suite shows. As a result, 20 of 192 ports score 0 on layout alone, and the unloadable count differs between target-on and target-off cells (B1).
2. **API agreement measures naming as well as behavior.** It compares rule class names (`RuleChar`) or tags (`"char"`) verbatim, so the two human references agree on only 76 of 999 cases (A1).
3. **The per-flag statistics run 135 uncorrected tests.** Their `minimum_detectable_gap` is the critical value, where the chance of detection is about one half, not a power-based size (S1, S2). The notebook now states both (PR #160); no correction is applied.

## Objections

Each objection opens with the measure in plain words: what is counted, over what, and what high and low values look like.

### Design

#### D1. **The target flag ships more than tests: project scaffolding and the reference interface come with it.**
Measure: the `include_target_integration_tests` flag, which is on or off per cell.
Evidence:
- With the flag on, the mount listings add `python/Makefile`, `python/pyproject.toml` and `python/uv.lock`, or `javascript/package.json` and `vitest.config.integration.ts` (`packages/gbnf_experiment/tests/integration/fixtures/shared/*.txt`).
- The generated suites import exactly what the held-out drivers require: `from gbnf import GBNF, RuleChar, RuleCharExclude, RuleEnd` and `import GBNF, { RuleType } from 'gbnf'`, with `{ "type": "end" }` expectations (gbnf `packages/gbnf/test/iteration/iteration.md` lines 3 and 8 at the pin).
Why it matters: the flag's effect on any measure is tests, plus runner, plus disclosed interface, and these cannot be separated. Folding the harness into the integration rules is Kevin's decision (journal 2026-09-28: "the suite is useless without its runner"); this objection concerns only its consequence for interpretation.
What would answer it: a cell that ships the scaffolding without the tests, or a statement in every per-flag table that the flag is the bundle.
Severity: weakens.

#### D2. **Prompt length varies by condition.**
Measure: the experiment prompt.
Evidence: `prompts/prompt.txt` differs across conditions only by `{suites_information}`, which is empty with no suites and one line per suite otherwise (`suites_information.py`, `suites.txt`).
Why it matters: the confound is part of the treatment (naming the suites), and it is small.
What would answer it: nothing beyond stating it.
Severity: cosmetic.

#### D3. **Each test has limited power at these sample sizes.**
Measure: `minimum_detectable_gap` in `analysis/notebook/src/stats.py:30`. It is the median gap that would reach p < 0.05.
Evidence: simulated with the repo's own `null_gaps` and `minimum_detectable_gap` on normal data with SD 1:
- the critical gap is 0.34 SD pooled (96 vs 96), 0.48 SD within one source language (48 vs 48), and 0.84 SD for one cell (12 vs 12);
- the chance of reaching p < 0.05 at a true 0.5 SD shift is 0.84 pooled and 0.52 within a language.
Why it matters: a p ≥ 0.05 within a language is uninformative for effects below about 0.5 SD.
What would answer it: the wording in S2. More runs per cell would also answer it, which is Kevin's call.
Severity: weakens.

#### D4. **The porter and the graders differ in effort but come from one model family.**
Measure: the efforts used.
Evidence:
- runs at medium effort (manifests);
- the judge at max (`analysis/judge/src/judge/cli.py:22-23`);
- walkthroughs at high (`analysis/walkthroughs/src/walkthroughs/cli.py:14-15`).
All three use `claude-opus-5-5`.
Why it matters: see J1 and W4.
What would answer it: see J1.
Severity: weakens.

#### D5. **Kept runs come from two harness batches, and auth mode is unrecorded.**
Measure: the manifest's `harness` and the matrix jsonl.
Evidence:
- Study 1 ran at commit `353d5b3`. The refills ran at `87066d8`, which only adds `--auth/--resume/--runs` to `scripts/study_test_configurations.py`.
- All 192 manifests say `dirty: true`.
- `--auth api-key|subscription` is written to neither the jsonl nor the manifest.
- Refills make up between 4 and 7 of each cell's 12 runs.
Why it matters: batch is partly confounded with cell. The dirty diff and the auth mode cannot be reconstructed.
What would answer it: record auth and the dirty diff in the manifest (`packages/` and `scripts/`, so this needs Kevin). Alternatively, compare batch 1 against refills within a cell.
Severity: weakens.

### Data

#### X1. **Exclusions are mostly non-informative, except exit 137.**
Measure: attempts excluded per cell (non-zero exit) before 12 successes.
Evidence:
- Study 1 (`matrix-20261012T021310Z.jsonl`) had 67 exit 1 and 6 exit 137 among 192 attempts.
- The exit-1 failures are "Credit balance is too low" API errors. 66 of 67 ended within 107 s (median 39 s).
- All 8 exit-137 kills across study and refills are in javascript-source cells (3, 3, 1 and 1). Their median wall time is 306-340 s, against 400 s for exit 0.
Why it matters: credit failures end before work, so they do not select on the port. A kill does select on the run. Refilling until 12 successes keeps only the runs that finished.
What would answer it: report exit-137 per cell beside every per-cell result. The notebook's `v2_failures` table does this.
Severity: weakens for javascript-source cells; cosmetic elsewhere.

#### X2. **Duplicate and trivial ports: checked, none found.**
Measure: whether two kept runs are the same run, or a port is near empty.
Evidence: there are 192 distinct run directories. Ports have 16-83 files and 36-375 KB of source.
Severity: none (holds).

#### X3. **The judge passes do not cover all 192 runs.**
Measure: items in `data/judge/<rubric>/manifest.json`.
Evidence:
- The code manifest has 190 run items. It lacks `20261012T120814Z_e20b3154` and `_fff7a32a`.
- The transcript manifest has 188. It also lacks `20261012T030049Z_fd28248f` and `20261012T114823Z_0e4ea4f3`.
- Both passes were launched with explicit `--runs` lists.
Why it matters: per-cell verdict counts will have n below 12 without saying so.
What would answer it: a top-up `judge run` on the missing runs once the passes finish. `judge run` skips ids already judged.
Severity: weakens.

### Held-out behavior (measure-behavior)

Measure: for 100 generated grammars and 799 inputs, whether the port accepts, rejects, errors or crashes. The score is the percent of pairs that match the hand-written reference in the port's target language. 100 means it agrees everywhere. A port that answers "reject" to everything scores 43-47.

#### B1. **The score depends on interface and layout, which the target flag discloses.**
Measure: held-out behavior agreement, the percent of 799 grammar and input pairs where the port answers accept, reject, error or crash as the human target-language port does.
Evidence:
- The python driver runs `from gbnf import GBNF, RuleEnd` with `PYTHONPATH=<port>` and treats only a raised `InputParseError` as reject (`analysis/measure-behavior/drivers/driver.py:9-15`).
- The typescript driver loads `src/index.ts` and checks `rule.type === "end"` (`driver.mts:8-17`).
- `driver_can_load` checks only `src/index.ts` (`analysis/notebook/src/Codebase.py:146`).
- 20 of 192 ports have no module at those paths and score 0 on every pair: 12 python ports use `src/gbnf/`, 1 uses `python/gbnf/`, and 7 typescript ports lack `src/index.ts`.
- Unloadable counts by target flag: python target 1/48 with the flag on and 12/48 with it off; javascript target 7/48 on and 0/48 off. Single cells range from 0 to 8 of 12.
Why it matters: a port that is right in behavior but laid out differently scores 0. Layout and naming are what the target suite reveals (D1), so the per-flag gap on this measure contains a layout term the measure cannot separate.
What would answer it: either a driver that finds the package by the port's own declarations (`pyproject` packages, `package.json` `main`/`exports`), or results reported only over loadable ports with the unloadable count beside them. Which layouts count as "the port" is a design decision.
Severity: blocks (for target-flag effects on behavior).

#### B2. **The two references disagree, and the score is defined against the target one.**
Measure: held-out behavior agreement, the percent of 799 grammar and input pairs where the port answers accept, reject, error or crash as the human target-language port does.
Evidence: reference-python against reference-typescript on the 799 pairs agree on 774 (96.9%). Of the 25 disagreements, 20 are accept/reject and 5 are error/reject (`analysis/measure-behavior/corpus/reference-*.jsonl`).
Why it matters: a port that is exactly faithful to its source can lose up to 3.1 points by design, and the loss differs by direction.
What would answer it: also score against the source-language reference. The outcomes already exist in the corpus, but the notebook caches only the report.
Severity: weakens (bounded at 3.1 points).

#### B3. **"error" matches "error" whatever the class.**
Measure: held-out behavior agreement, the percent of 799 grammar and input pairs where the port answers accept, reject, error or crash as the human target-language port does.
Evidence: `compare_outcomes.py` compares outcome categories only. The python reference itself raises `IndexError` on 25 pairs and `KeyError` on 5.
Why it matters: the measure is lenient on how a port fails. A port that fixes a reference bug is scored as disagreeing.
What would answer it: state it in the glossary. The class is already recorded in `error`.
Severity: cosmetic.

#### B4. **The constant-output floor is about 45%, not 0.**
Measure: held-out behavior agreement, the percent of 799 grammar and input pairs where the port answers accept, reject, error or crash as the human target-language port does.
Evidence: always-reject scores 43.4 (python) and 46.6 (typescript); always-accept scores 46.3 and 43.8.
Why it matters: the axis reads as 0-100 skill, but chance level is near 45.
What would answer it: a chance-corrected column (Cohen's kappa from the cached confusion table), or the floor drawn on the chart.
Severity: weakens.

#### B5. **The corpus is held out.**
Measure: held-out behavior and API agreement, which need inputs the agent never saw.
Evidence: the corpus is generated (`generate_corpus.py`, seed 0) and never mounted.
Severity: none (holds).

### Held-out API (measure-api)

Measure: for 999 cases, the rules or exception that each step through the port's public API returns. The score is the percent of cases where every step equals the target-language reference.

#### A1. **The rule's type is compared as a language-specific name.**
Measure: held-out API agreement, the percent of 999 cases where every step through the port's public API returns what the human target-language port returns.
Evidence:
- Python records `type(rule).__name__`, such as `RuleChar` (`analysis/measure-api/drivers/driver.py:15`); typescript records `rule.type`, such as `"char"` (`driver.mts:13`).
- `measure-api compare` of reference-python against reference-typescript gives 999 cases: 0 match, 866 mismatch, 76 error_match, 57 error_mismatch, so 76 agreements (7.6%).
Why it matters: the score is mostly whether the port picked the target human port's vocabulary for rule types. A python-target port that uses `type` tags, or a TS port that uses classes, scores near 0 whatever its behavior. That vocabulary is in the target suite (D1).
What would answer it: map each side's rule type into one vocabulary before comparing (`RuleChar`↔`char`, `RuleCharExclude`↔`char_exclude`, `RuleEnd`↔`end`), and report the unmapped score beside it. This changes what the measure measures, so it needs Kevin.
Severity: blocks.

#### A2. **API has the same loader and layout coupling as B1.**
Measure: held-out API agreement, the percent of 999 cases where every step through the port's public API returns what the human target-language port returns.
Evidence: it uses the same `driver_can_load` and the same import paths.
Severity: blocks (as B1).

### AST drift (measure-ast)

Measure: functions in the port paired by normalised name and arity with the human port in the same (target) language.
- `ast_matched_fraction` is the share of reference functions paired. 1 means every reference function has a same-named port function.
- Tree edit distance compares the shapes of paired functions (0 is the same shape).
- Call paths compare who-calls-whom from the public entry points. `ast_mean_edge_recall` of 1 means every reference call edge is in the port.

#### T1. **Method calls on builtins pollute the call graph.**
Measure: call-path edge recall and trace distance: how many of the human port's who-calls-whom links from its public entry points the port also has, and how far apart the two call sequences are.
Evidence: `callee()` drops the receiver (`analysis/measure-ast/src/measure_ast/call_graph.py:92-103`), so `seen.add(x)` resolves to every package function named `add` that fits. Across the 193 cached reports, `add`, `get` and `has` are the callee in 45,911 of 144,255 missing or extra edges (32%).
Why it matters: edge recall and trace distance carry noise that depends on how often a port calls `set.add`, `dict.get` and `map.has`, not on its structure.
What would answer it: do not resolve a builtin collection method name called through a receiver that is not `self`, `this` or a known class.
Answer: fixed in PR #154 (`65e670a3`). A method call is dropped when its receiver is bound to a builtin constructor or literal. Limits: bindings ignore scope and reassignment, module-level bindings are not seen, and a package class named like a builtin (`Map`) is treated as the builtin. Cached AST reports predate the fix; the AST cache key hashes `measure-ast/src`, so they recompute.
Severity: weakens.

#### T2. **Name pairing rewards keeping names.**
Measure: `ast_matched_fraction`, the share of the human port's functions that have a port function of the same normalised name and arity.
Evidence: pairing is by `name.lstrip("_#").replace("_","").lower()` and arity (`pair_functions.py`). Port-only functions have a median share of 0.257 (0.088-0.372) of named functions.
Why it matters: an idiomatic rename reads as a missing function plus an extra one. The notebook already says "Every number measures structural drift from the reference, not fidelity" (`analysis/notebook/runs.py:2659`), and the chart titles say "counterpart" and "distance". No title says fidelity.
What would answer it: conceded as the definition of drift. The titles already hold.
Severity: cosmetic.

#### T3. **The AST reference is an independent human port, not the source.**
Measure: every AST drift number; each compares the port with the human port in the target language.
Evidence: `run_measure_ast_compare` compares against `pinned_reference()/packages/gbnf/<target>`, as the notebook states (`runs.py`, "AST relative to the reference").
Why it matters: drift includes the human porter's own choices.
What would answer it: conceded as a limit. It is stated in the notebook.
Severity: cosmetic.

### Transcript measures (measure-transcript)

Measure: counts parsed from each run's tool calls, such as the source files read before the first write into `/target`, rereads, suite runs and own tests. `first_read_is_entry_point` is whether the first source code file read is the package's entry point.

#### R1. **The read detector missed shell loops and globs, so 115 of 192 runs had a null entry-point reading.**
Measure: `first_read_is_entry_point` and the read counts, built from which files each tool call reads.
Evidence: as of `4e3bd4e`, `for f in ...; do cat $f` counted as one read of `.../$f`, `tail` was not a reader, and option values were taken as paths.
Answer: fixed in PR #151 (`bf020a2`). Nulls fell from 69/46 to 9/14 (python/javascript).
Residual:
- unsorted `$(find ...)` loops are left as written, because their print order is unrecorded (21 runs);
- `find -size` (2 runs);
- `case ... continue` skips;
- reads inside `python -c` and heredocs.
Severity: weakens (residual).

#### R2. **"Before the first write" counts any write under `/target`.**
Measure: `files_read_before_first_write`, the source files the agent read before it first wrote into the port.
Evidence: `first_write_turn` is the first Write, Edit, redirect or `tee` under `/target` (`measure_transcript.py`). A scratch note or a copied test counts.
Why it matters: `files_read_before_first_write` is split at an event that may not be porting.
What would answer it: conceded as a limit. A first write of a non-test code file would be a sharper split.
Severity: weakens.

### LLM judge

Measure: for each port, one blind `claude` call compares the source reference (A) with the port (B) on a fixed rubric (`rubrics/code.md`), giving verdicts and a 1-5 fidelity score. For each transcript, one call answers fixed questions on cheating, tests run and reading strategy (`rubrics/transcript.md`).

#### J1. **The judge is the porter's own model.**
Measure: the code judge's verdicts and 1-5 fidelity score, and the transcript judge's cheating verdicts.
Evidence: both are `claude-opus-5-5` (`analysis/judge/README.md`, "The judge").
Why it matters: self-preference can inflate fidelity and depress cheating verdicts.
What would answer it: a second judge family on the double-judge subsample. Only the `claude` CLI is wired, so this needs Kevin.
Severity: weakens.

#### J2. **Each item has one judgment, so the judge's own noise is unknown.**
Measure: every judge verdict.
Evidence: `run_judge.py` judges each id once, and a rerun skips ids already judged.
Why it matters: a verdict gap between flags cannot be told from judge noise.
What would answer it: judge a seeded 10% subsample (always including the baselines) a second time and report agreement per verdict as Cohen's kappa.
Answer: partly fixed in PR #158 (`968d0b9f`). `judge run --replicate-fraction F` (default 0) judges every baseline plus the items whose id hashes below F a second time into `replicates.jsonl`, with the same prompt, schema, model and effort. Still open: a replicate pass on the current judgments, and kappa in `judge report`.
Severity: blocks (for any judge comparison).

#### J3. **The baseline is two draws.**
Measure: the code judge's verdicts on the human pair, the baseline a port's verdicts are read against.
Evidence: the code rubric's baseline is the human pair once in each direction (`build_items.py:24-25`), with no repeat. The transcript rubric has no baseline (README).
Why it matters: the human pair's verdicts have unknown spread.
What would answer it: the J2 subsample always includes both baselines. The transcript baseline is conceded: there is no human transcript.
Answer: PR #158 always replicates both baselines when F > 0. Open until a replicate pass runs.
Severity: weakens.

#### J4. **The port is always side B.**
Measure: the code judge's verdicts, which compare side A (the source) with side B (the port).
Evidence: `code_item(reference / source, run / "ported_implementation")` (`build_items.py:27`).
Why it matters: position effects in LLM judges are documented, and here position is fully confounded with role.
What would answer it: judge a subsample with the sides swapped. This doubles calls on that subsample, so it needs Kevin.
Severity: weakens.

#### J5. **The transcript items omit subagent transcripts.**
Measure: the transcript judge's verdicts on cheating, tests run and reading strategy.
Evidence: `sorted((run / TRANSCRIPTS).glob("*.jsonl"))` reads only the top level (`build_items.py:31`). 59 of the 192 runs have 97 nested subagent `.jsonl` files under `transcript/.claude/projects/-target/`. measure-transcript merges them.
Why it matters: the cheating, tests-run and reading verdicts cannot see subagent actions in 31% of runs.
What would answer it: include the nested files in order. This changes those 59 items' ids, so the running pass would need a re-judge of 59 items; that needs Kevin.
Severity: blocks (for transcript verdicts on those runs).

#### J6. **Tool input is cut at 2,000 characters.**
Measure: the transcript judge's verdicts, read from the tool calls in the transcript.
Evidence: `LIMIT = 2000` (`analysis/judge/src/judge/transcript_item.py:4`).
Why it matters: "hard-coding expectations" and "editing tests to pass" are judged from Write and Edit content, which a cut can hide. The share of inputs cut is not counted, because that would require parsing transcripts.
What would answer it: count the cut inputs per run in the manifest. Raising the limit changes ids, so it needs Kevin.
Severity: weakens.

#### J7. **The code rubric's verdicts are forced.**
Measure: the code judge's verdicts, each one value from a fixed list.
Evidence: `rubrics/code.schema.json` enums have no abstain value. The transcript schema has `confidence` and `unsure`.
Why it matters: an unsure judge must pick a side.
What would answer it: conceded. The J2 kappa shows how stable the forced picks are.
Severity: cosmetic.

#### J8. **Condition leaks into code items only marginally.**
Measure: the code judge's verdicts, which should not reveal which tests the port was given.
Evidence: after `source_files.py` excludes, 8 of 192 ports still contribute test-like paths (`scripts/`, `src/test-utils/`, `tools/`) to side B.
Why it matters: the judge could infer a flag from leftover test helpers.
What would answer it: conceded. The leak is small.
Severity: cosmetic.

### Walkthroughs

Measure: an LLM writes, for each public entry point, ordered one-sentence steps (happy path, error paths, invariants) for the reference and for the port. Steps are matched by embedding cosine ≥ 0.8.
- `mean_coverage` is the share of reference steps that have a matching port step. 1 means every step the reference walkthrough lists also appears in the port's.
- `mean_order_agreement` is the share of matched steps that come in the same order.

#### W1. **The noise floor sits close to the cross-language baseline.**
Measure: `mean_coverage`, the share of the reference walkthrough's steps that the port's walkthrough also has. 1 means all of them.
Evidence: `data/walkthroughs/reference/reference-lines.json`:
- the same code explained twice reaches happy-path coverage 0.63 (python) and 0.70 (javascript);
- the two human ports against each other reach 0.61 and 0.52;
- each figure is one draw;
- the threshold sweep (W3) on the python reference lines gives same-code against human-pair coverage of 0.758/0.777 at 0.7, 0.747/0.735 at 0.75, 0.632/0.615 at 0.8, 0.549/0.348 at 0.85 and 0.464/0.242 at 0.9. Whether the floor separates from the baseline depends on the cut.
Why it matters: the measure spans 0.02-0.18 between "same code" and "independent human port". With a single reference draw, a port's coverage mixes walkthrough noise into the comparison.
What would answer it: compare every port against both reference draws (`a` and `b`), report both, and add more repeat draws to estimate the floor's spread.
Severity: blocks (until the floor has a spread).

#### W2. **Order agreement is uninformative.**
Measure: `mean_order_agreement`, the share of matched steps that come in the reference's order.
Evidence: 215 of 255 aligned sections across the compare outputs have at most one match, and the longest increasing run of one match is 1. 97 sections have no matches (order is null). Happy-path `mean_order_agreement` is 1.0 in every reference line.
Why it matters: an order measure needs at least three matches to say anything.
What would answer it: report order only for sections with three or more matches, with their count.
Severity: blocks (for order).

#### W3. **The 0.8 threshold has no sweep.**
Measure: every walkthrough match, which counts two steps as the same when their embedding cosine is at least 0.8.
Evidence: `pick_similarity.py:14`.
Why it matters: coverage is a step function of the threshold, so a single cut can create or erase gaps.
What would answer it: a sweep in `walkthroughs compare`.
Answer: fixed in PR #156 (`101f5691`). Every compare output and reference line now carries `sweep`: coverage, order and per-section counts at the threshold −0.1, −0.05, 0, +0.05 and +0.1. Compares written before the merge have no sweep, and the running walkthroughs pass uses the main checkout as it was at launch.
Severity: weakens.

#### W4. **The writer is the porter's model family.**
Measure: every walkthrough number; the walkthroughs are written by an LLM.
Evidence: `claude-opus-5-5` at high (`cli.py:14-15`).
Why it matters: the walkthrough of a port and of a reference may share phrasing for reasons unrelated to code.
What would answer it: conceded. W1's floor bounds it.
Severity: weakens.

#### W5. **The embedding configuration is unrecorded in compare outputs.**
Measure: every walkthrough match, which depends on the embedding server's vectors.
Evidence:
- The compares already written used the local CPU container `walkthroughs-embed`: `Qwen3-Embedding-0.6B-Q8_0.gguf`, `--pooling last`.
- Kevin: "Embedding server should run on tower. There is a GPU". Tower now serves the same gguf (639,150,592 bytes) with pooling last. One sentence embedded locally and on tower has cosine 0.99971, so a Q8_0 versus f16 difference does not arise.
- The request's model string `qwen3-embedding-0.6b-q8_0` (`embed_text.py:9`) is a label that a single-model llama-server ignores.
- The compare output records only `similarity` and `threshold`.
- llama-server's `/props` reports the model path and quantisation, but not pooling. Tower is a llama.cpp router, whose `GET /v1/models` lists each model's launch arguments, `--model` and `--pooling` included.
Why it matters: a later server change would change the vectors silently. Whether 0.8 means the same under another pooling is untested.
What would answer it: record the endpoint, model file and pooling in every compare output.
Answer: fixed in PR #155 (`a187fb7e`). Every compare output carries `embeddings`: the url, the requested model and the server's `/models` entry. On tower (`qwen3-embedding-0.6b-q8_0.gguf`, `--pooling last`) the python reference-lines noise floor reproduces the local container's to six places (0.632051). The notebook's embedding cache is keyed the same way (C4).
Severity: weakens.

#### W6. **Every port is compared against reference walkthrough `a` only.**
Measure: `mean_coverage` against the reference walkthrough.
Evidence: every `data/walkthroughs/compare/*.json` names the tag-`a` file for its language. The python `a` and `b` draws list 15 and 13 entry points.
Why it matters: the reference's entry-point set itself varies by draw. See W1.
What would answer it: as W1.
Severity: weakens.

### Statistics

Measure: per flag, the median of the runs with the flag on minus the median with it off. The test shuffles the labels 10,000 times and reports p, a 95% bootstrap interval, and `minimum_detectable_gap`.

#### S1. **There are 135 uncorrected tests.**
Measure: the per-flag p: the share of label shuffles that give a median gap at least as large as the observed one.
Evidence:
- `V2_LEADS` has 15 measures (`runs.py:1144`). Each gets 3 flags × 3 scopes (pooled, python, javascript) = 9 rows (`flag_comparison`, `runs.py:1225`), so 135 p-values at α = 0.05.
- About 7 rows are expected below 0.05 if no flag affects anything.
- The Spearman table and matrix add one rank correlation per pair of varied measures, also uncorrected.
Why it matters: a single p < 0.05 row is weak evidence.
What would answer it: a multiplicity note, and Benjamini-Hochberg q over the family.
Answer: note added in PR #160 (`47c9b8ed`). It counts the rows with a p (135 when every row has runs), states that about 7 fall below 0.05 with no effect, and calls every p exploratory. No q values are computed.
Severity: blocks (for reading single rows).

#### S2. **`minimum_detectable_gap` is the critical value, not a detectable size.**
Measure: `minimum_detectable_gap`, the median gap above which p < 0.05.
Evidence: `stats.py:30-36` returns the gap at which p would be just below 0.05. At that true gap, p < 0.05 about half the time (D3).
Why it matters: "minimum detectable" is read as an 80%-power effect size.
What would answer it: say so in the table's reading.
Answer: fixed in PR #160 (`47c9b8ed`). The reading calls it the critical value and says a true gap of that size clears it about half the time.
Severity: weakens.

#### S3. **The pooled shuffles ignore source language.**
Measure: the pooled per-flag p, over both source languages.
Evidence: `flag_comparison` pools both languages and shuffles labels across them (`runs.py:1225-1232`).
Why it matters: the design is balanced (48 on and 48 off per language), so the test stays valid, but it loses power when language shifts the measure.
What would answer it: shuffles stratified by source language. Conceded: it is conservative, not wrong.
Severity: cosmetic.

#### S4. **The bootstrap of a median at n = 48-96 is coarse.**
Measure: `low` to `high`, the 95% bootstrap interval on the median gap.
Evidence: `bootstrap_interval` takes percentiles of resampled medians (`stats.py:39-50`), whose distribution is discrete at these sizes.
Why it matters: the interval's coverage is approximate.
What would answer it: conceded. The permutation p carries the test.
Severity: cosmetic.

#### S5. **The Spearman table includes components of its own lead.**
Measure: the Spearman table, how each per-run measure ranks against held-out behavior agreement.
Evidence: `v2_measures` includes the `reference_<a>_port_<b>` confusion counts (`runs.py:1236-1239`), which sum to the pairs that `behavior_agreement_pct` is computed from.
Why it matters: some correlations with the lead hold by definition.
What would answer it: a sentence in the Spearman reading saying so. Not yet written: the PR #160 note covers the flag tests only.
Severity: cosmetic.

#### S6. **The IQR per cell rests on 12 points.**
Measure: the per-cell interquartile range, the middle half of a cell's runs.
Evidence: `v2_summary` takes the 0.25 and 0.75 quantiles of n = 12.
Severity: cosmetic (conceded).

### Caches and reproducibility

#### C1. **The behavior and API caches are keyed on the port alone.**
Measure: behavior and API agreement as the notebook reads them from its cache.
Evidence: `behavior_cache` and `api_cache` paths are `codebases/{behavior,api}/<port hash>.pkl` (`analysis/notebook/src/Codebase.py:60-61`). A change to a driver, the corpus or a reference outcome file would serve stale reports.
What would answer it: key both caches on the measure package's source and corpus as well, as `ast_cache` does.
Severity: weakens.

#### C2. **The AST cache key omits tree-sitter versions.**
Measure: every AST number as the notebook reads it from its cache.
Evidence: `MEASURE_AST_VERSION = content_hash(MEASURE_AST_DIR / "src")` (`Codebase.py:116`). Tree-sitter is pinned in `analysis/measure-ast/uv.lock` (0.25.2, python grammar 0.25.0, typescript 0.23.2), but the lock is not hashed.
What would answer it: hash `pyproject.toml` and `uv.lock` into the key.
Severity: cosmetic.

#### C3. **The pinned reference checkout is keyed on the commit alone.**
Measure: every AST number; each is computed against a checkout of the human port.
Evidence: `pinned_reference()` returns any existing `reference/<GBNF_COMMIT>` directory (`Codebase.py:251-254`). A changed patch in `gbnf-prepare/patches` would not reach it.
What would answer it: key the checkout on the commit and the patches' hash.
Severity: weakens.

#### C4. **The V1 embedding caches record a model label only.**
Measure: V1 embedding distance between a port and the reference, from cached vectors.
Evidence: `~/.cache/ports/analysis/embeddings/*/index.json` carries `model: qwen3-embedding-0.6b-q8_0` and `dims`. It records no server, quantisation or pooling.
What would answer it: key the cache on the model file and pooling, and check the old vectors against a known server.
Answer: fixed in PR #159 (`4d2940bc`). The cache directory is `embeddings-stripped/qwen3-embedding-0.6b-q8_0-pooling-last/`, and the notebook refuses a server whose `/models` entry reports another file or pooling. Re-embedding a seeded sample of 50 cached files (10 reference, 40 V1 run) on tower at q8_0, pooling last, gives cosine 0.99957-0.99999 to the cached vectors; one sentence embedded locally and on tower under one known configuration gives 0.99971. The old vectors were adopted under the new key on that evidence. No other pooling was tried, so the check shows agreement with this configuration, not how far another would differ.
Severity: weakens (V1 only).

#### C5. **`export_charts.py` determinism is unverified.**
Measure: the exported chart files.
Evidence: running it twice requires the notebook's embedding work.
Severity: unverified.

#### C6. **The V1 embedding pair export depends on a reference checkout outside the repo that no longer exists.**
Measure: V1 embedding distances from `export_embedding_pairs.py`, which checks each cached vector set against its source before use.
Evidence:
- The source is `~/.cache/ports/gbnf-experiment/prepared/771a734d60ecbae5/source/<language>`, a hard-coded hash (`analysis/notebook/src/corpus.py:15`). That directory is gone on the analysis machine.
- The export failed with `cached file selection differs from source`: the source listing was empty. The 35 python and 37 typescript cached reference files are intact.
Why it matters: the V1 embedding comparisons cannot be revalidated or exported, and the error named the wrong cause.
What would answer it: rebuild the prepared checkout with the experiment's prepare step and confirm it reproduces hash `771a734d60ecbae5`. That runs `packages/` code, so it needs Kevin.
Answer: the error is fixed in PR #161 (`871c5ba8`). A missing source now raises `FileNotFoundError` naming the path.
Severity: weakens (V1 only).

## Table

| # | Claim | Severity | Status |
|---|---|---|---|
| D1 | Target flag ships scaffolding and the interface | weakens | needs Kevin |
| D2 | Prompt length varies by condition | cosmetic | conceded as a limit |
| D3 | Limited power at these n | weakens | conceded as a limit; wording fixed in PR #160 (`47c9b8ed`) |
| D4 | One model family porter and graders | weakens | conceded as a limit |
| D5 | Two harness batches, dirty trees, auth unrecorded | weakens | needs Kevin |
| X1 | Exit-137 exclusions select on the run | weakens | control added (`v2_failures`) |
| X2 | Duplicates or trivial ports | none | holds |
| X3 | Judge passes miss 2 and 4 runs | weakens | needs Kevin (top-up run) |
| B1 | Behavior depends on interface and layout | blocks | needs Kevin |
| B2 | References disagree on 25 of 799 pairs | weakens | conceded as a limit (≤ 3.1 points) |
| B3 | Any error matches any error | cosmetic | conceded as a limit |
| B4 | Floor near 45%, not 0 | weakens | open |
| B5 | Corpus held out | none | holds |
| A1 | Rule type compared as a language-specific name | blocks | needs Kevin |
| A2 | API layout coupling | blocks | needs Kevin |
| T1 | Builtin method calls pollute call graphs | weakens | fixed in PR #154 (`65e670a3`) |
| T2 | Name pairing rewards kept names | cosmetic | conceded; titles hold |
| T3 | AST reference is a human port | cosmetic | conceded as a limit |
| R1 | Read detector missed loops and globs | weakens | fixed in PR #151; residual conceded |
| R2 | First write is any write | weakens | conceded as a limit |
| J1 | Judge is the porter's model | weakens | needs Kevin |
| J2 | One judgment per item | blocks | flag added in PR #158 (`968d0b9f`); replicate pass and kappa open |
| J3 | Baseline is two draws | weakens | flag added in PR #158 (`968d0b9f`); open until a replicate pass |
| J4 | Port always side B | weakens | needs Kevin |
| J5 | Transcript items omit subagents | blocks | needs Kevin |
| J6 | Tool input cut at 2,000 characters | weakens | needs Kevin |
| J7 | Forced code verdicts | cosmetic | conceded as a limit |
| J8 | Test helpers leak into 8 code items | cosmetic | conceded as a limit |
| W1 | Noise floor close to baseline | blocks | needs Kevin (more draws) |
| W2 | Order agreement uninformative | blocks | needs Kevin |
| W3 | No threshold sweep | weakens | fixed in PR #156 (`101f5691`) |
| W4 | Writer is the porter's family | weakens | conceded as a limit |
| W5 | Embedding config unrecorded | weakens | fixed in PR #155 (`a187fb7e`) |
| W6 | Only reference draw `a` | weakens | needs Kevin (with W1) |
| S1 | 135 uncorrected tests | blocks | note added in PR #160 (`47c9b8ed`); no correction |
| S2 | Detectable gap is the critical value | weakens | fixed in PR #160 (`47c9b8ed`) |
| S3 | Pooled shuffles ignore language | cosmetic | conceded as a limit |
| S4 | Median bootstrap coarse | cosmetic | conceded as a limit |
| S5 | Spearman includes lead components | cosmetic | open |
| S6 | IQR on 12 | cosmetic | conceded as a limit |
| C1 | Behavior and API caches keyed on port only | weakens | open |
| C2 | AST key omits tree-sitter | cosmetic | open |
| C3 | Reference checkout keyed on commit only | weakens | open |
| C4 | V1 embedding caches unrecorded | weakens | fixed in PR #159 (`4d2940bc`) |
| C5 | Chart export determinism | unverified | unverified |
| C6 | V1 embedding export's reference checkout is gone | weakens | error fixed in PR #161 (`871c5ba8`); rebuild needs Kevin |
