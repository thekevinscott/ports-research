# Literature synthesis — ★ shortlist (2026-07-02)

Step 2 of HANDOFF.md. Sources: the nine ★ papers in `papers/INDEX.md`, read in full.

## The synthesis (one paragraph)

Differential equivalence-checking of LLM-translated code is *validated as a finding* but does
not exist as *a tool you can use*. The evidence that it's necessary is strong: differential
fuzzing finds 19–35% of LLM refactorings non-equivalent, and ~21% of those pass the project's
entire existing test suite (Eq@DFuzz); LLM translation introduces vulnerabilities at 28.6–45%
per pass, with SAST under 60 F1 and human reviewers at chance (security-centric study); the
canonical bug taxonomy (Lost in Translation, ICSE'24) puts data-representation bugs — numeric
width, parsing, formatting — as the largest class at 33.5%. But every validation pipeline in
the literature is ad hoc and per-paper: the TOSEM survey (57 studies, 2020–2025) finds test-based
"computational accuracy" the dominant oracle, static metrics (BLEU/CodeBLEU) still the most
*used* despite being explicitly discredited, and no shared equivalence harness anywhere.
The closest artifacts each miss the target on a different axis: RustAssure is open-source but
welded to C→Rust via LLVM/KLEE symbolic execution (no common IR exists for Python/TS, and it's
per-function, stateless); Eq@DFuzz is Python-to-Python only with no released artifact;
BabelCoder's source-execution-as-oracle works (94% CA) but is one-shot, function-level, and its
"spec" is LLM-generated pseudocode derived from the code itself — circular; RustPrint's
documentation-guided migration extracts docs *from* code post-hoc and judges equivalence with an
LLM, then names differential and property-based testing as its own future work. Three things are
*entirely* absent from this literature: (1) **maintenance over time** — every paper is one-shot
migration; the only paper addressing drift-triggered revalidation (environment-in-the-loop) is
an unimplemented position paper; (2) **N-way peer implementations** — no paper maintains or
cross-checks more than a source→target pair; the nearest relative, metamorphic prompt testing,
is a regenerate-and-vote scheme that *suffers from* consensus-wrong rather than detecting it;
(3) **measurement with synthetic ground truth** — the Csmith playbook has never been applied to
LLM translation; every paper's ground truth is benchmark test suites, which Lost-in-Translation
itself shows are weak oracles (success detection correlates r=0.64–0.85 with tests-per-sample).
The gap is exactly as hypothesized, and wider: not just "no clean open-source tool," but no
tool that is language-agnostic, stateful, maintenance-oriented, or measurable — the four
properties the harness is designed around.

## What's productionized vs open, per layer of the planned harness

| Harness layer | State of the art | Open gap |
|---|---|---|
| Differential testing | Proven to catch what test suites miss (Eq@DFuzz 21%); RustAssure open-source for C→Rust only | No language-agnostic harness; nothing stateful (op sequences); nothing for Python/TS/Rust triples |
| Doc-as-spec | RustPrint: post-hoc doc *extraction* + LLM-judged equivalence, 93–98% feature preservation | Authored, executable (doctest), coverage-gated docs as contract — no counterpart; RustPrint admits behavioral bugs are invisible to doc comparison |
| Property/metamorphic | Metamorphic *prompt* testing (75% recall, 8.6% FP) is consensus voting, not program-level relations | Program-level metamorphic relations for consensus-wrong detection — deliberately avoided by the one paper in this space ("finding per-program relations is hard") |
| Security gate | SAST <60 F1, humans ~chance, multi-LLM judge 82.6 F1 (best, still advisory-grade) | Dominant vuln classes (dropped validation semantics, API mapping, missing encoding) invisible to dependency scanners AND crash fuzzing; differential testing on adversarial inputs (encodings, boundaries, traversal strings) is the untried fit |
| Measurement | Benchmark test suites as ground truth, universally; known-weak (r=0.64–0.85 oracle sensitivity to test count) | Synthetic ground-truth generation (Csmith playbook) unapplied to translation; no endogeneity-free sensitivity measurement anywhere |
| Maintenance over time | Nothing implemented. Environment-in-the-loop (position paper): CI-triggered revalidation on drift, unbuilt | The entire dimension. "Human cost per re-sync → 0" has no baseline in the literature |

## Design consequences (what the papers change about the plan)

1. **Keep the uniform JSON driver; skip symbolic execution.** RustAssure sidesteps
   cross-language value comparison by comparing symbolic expressions over shared LLVM IR — that
   trick is unavailable for Python/TS. Concrete-output comparison with canonical serialization
   is the only route, which confirms canonicalization as the load-bearing subtlety (HANDOFF
   already flags this).
2. **Stateful op sequences are novel, not incremental.** Everything in the literature tests
   single functions on single calls. The op-sequence driver is the cheapest real differentiator.
3. **Generator axes, updated from the taxonomy.** Confirmed by data: numeric width/precision,
   input parsing, output formatting, container element types, mutability of returned
   collections, API-behavior mismatch (accumulate/reduce semantics), added/removed logic.
   NOT in the measured taxonomy (benchmarks were stdin batch programs): unicode, recursion,
   statefulness — keep them as axes but expect to *establish* their failure rates, not confirm
   published ones. Neither TS nor Rust appears as an LLM-translation target in the taxonomy
   study; the Rust/Python/TS triple is unmeasured territory.
4. **Oracle-strength is itself the published weakness.** Lost-in-Translation's r=0.64–0.85
   correlation between test count and detected failures is the citable justification for the
   whole measurement methodology: benchmark oracles are too weak to measure equivalence, so
   ground truth must be synthetic.
5. **Test-transplant as a rigor pattern.** RustPrint's cross-eval (adapt system A's tests to
   system B's output to kill self-alignment bias) is directly reusable when comparing harness
   variants or agentic re-port loops later.
6. **Security layer: reweight.** cargo-audit/npm-audit catch dependency CVEs, which are ~none
   of the translation-introduced vuln taxonomy. The differential layer fed with adversarial
   input classes (encodings, boundary values, traversal strings) targets the actual top classes
   (input validation 34.9%, API misuse 32.7%, output encoding 17.8%). Keep SAST but expect
   leak-and-false-block; LLM review stays advisory (82.6 F1 ceiling).
7. **Determinism precondition confirmed the hard way.** BabelCoder's oracle only works because
   the source is runnable and deterministic; RustAssure excludes IO/nondeterminism entirely.
   Nobody has a story for nondeterministic APIs — constrain the library choice, don't fight it.

## Per-paper notes

### neural-code-translation-survey (TOSEM, SLR of 57 studies 2020–2025)
Field map: fine-tuning (22) > scratch (17) > prompting (16) > agents (1) + RAG (1, both "early
stage"). 74% of studies are function/method-level; class/module (6) and repo-level (8) immature.
Validation is ad hoc per paper: test-based CA (17 studies), pass@k (5), static metrics most
common (BLEU 42%) and explicitly criticized. Maintenance over time: absent — everything one-shot.
Closest prior art to the harness: Eniser et al. AAAI'24 (NOMOS, property-based testing of
translation models), TransMap (FSE'23, line-level semantic-mistake pinpointing), Cotran
(ECAI'24, symbolic execution + FEqAcc). Tang et al.: fixing broken TransCoder tests shifted
results ~10% — measured ground-truth fragility. Follow-ups: PolyHumanEval (14 langs incl.
Rust/TS), ClassEval-T, AlphaTrans (repo-level, FSE'25), LessLeak-Bench (data leakage).

### environment-in-the-loop (ReCode'26 workshop)
**Position paper — no implementation, no experiments.** Three-agent loop: M-Agent (migrate),
E-Agent (build reproducible env, route errors: config→self-repair, semantic→M, behavioral→T),
T-Agent (generate/run tests). Oracle is just "generated+legacy tests pass"; behavioral
equivalence asserted, never operationalized. Reusable: the error-routing taxonomy
(env-broke vs code-diverged), CI-triggered revalidation on dependency drift (= the over-time
dimension, unbuilt), env-anchored diagnostics. Citable motivation, zero measurement content.

### babelcoder (GPT-4o, 4 benchmarks, 5 languages)
"Spec" = LLM-generated line-by-line pseudocode of the source (not human docs — circular:
inherits source bugs). Oracle = execute source on LLM-generated inputs, record outputs as
expected (source-execution-as-oracle differential). State machine competes raw-source vs
NL-spec input on per-iteration pass rate. Avg CA 94.16%; ablation: spec layer +6.4 points,
validation and SBFL localization <1 each. ~$0.045/correct translation. Function/file-level
only; example-based I/O only, no properties. Their CA comparability policy (exact string match,
3-decimal float rounding) is a primitive canonicalization policy — ours must be principled.

### documentation-guided-c-to-rust (RustPrint; 8 C repos 11–84K LoC)
Docs are *generated from the C source* (CodeWiki-derived), feature-hierarchy rubric trees,
1 feature = 1 crate; refinement compares re-generated docs of Rust output vs source docs
(LLM-as-judge). Compiles 8/8 where Self-Repair/EvoC2Rust compile 0/8; feature preservation
93–98% vs Claude Code 49–53%. No output-vs-C differential execution — validation is transplanted
test suites. Admits: "many migration bugs are behavioral rather than documentary"; names
differential + property testing as future work. Test-transplant cross-eval protocol is the
reusable rigor pattern.

### rustassure-differential-symbolic (open-source: github.com/davsec-lab/rustassure)
Per-function differential *symbolic* testing: C and Rust → LLVM IR → KLEE, compare normalized
symbolic-expression graphs by edit distance (not SMT — no proof). Handles representation
differences structurally (repr(C,packed), Option unwrapping, fat-pointer extraction) — a trick
unavailable without shared IR. GPT-4o: 72% symbolically equivalent; found 25 bugs; precision
~86–88%, recall 100% on the two hand-labeled codebases; FLUORINE (differential fuzzing) found
1 of their 20. Cost: 5–15h per codebase. Stateless, single-call, no floats discussed, IO
excluded.

### differential-fuzzing-equivalence-refactorings (Eq@DFuzz, UVA)
6 LLMs × HumanEval/MBPP/APPS × 2 refactoring prompts = 3,538 analyzed refactorings. GPT-4
infers input constraints, Atheris fuzzes (1–2K inputs), binary oracle: one mismatch →
non-equivalent. 19–35% non-equivalent per model (GPT-4o best 18.6%); of flagged
non-equivalences, ~21.65% pass the dataset's full test suite — even APPS with 21.2 tests/problem
misses at the same rate (tests are redundant, not diverse). Python→Python only, stateless
benchmark functions, no artifact released, no qualitative taxonomy (deferred to future work).
Strongest citable motivation for the whole project.

### metamorphic-prompt-testing (UTSA; GPT-4, HumanEval)
One relation, at the *prompt* level: paraphrase the prompt N ways, generate N programs, fuzz
≤20 inputs from the target, majority-vote disagreement → flag. 75% recall / 8.6% FP / 60%
precision at N=5. Explicitly avoids program-level metamorphic relations ("finding per-program
relations is hard"). Structurally this is consensus voting — it *suffers from* consensus-wrong
(their false negatives are exactly paraphrase-clustering: all variants share the same wrong
semantics). The ports-as-paraphrases analogy holds for the differential layer; the
consensus-wrong layer (program-level properties) has effectively no prior art. No artifact.

### lost-in-translation-bugs (Pan et al., ICSE 2024; 1,748 labeled GPT-4 bugs)
15-category taxonomy: data-related largest at 33.5% (incorrect type 11.5%, input parsing 18.1%,
output formatting 3.9%); syntactic/semantic PL differences 30.5%; dependency & logic 24.2%.
Failed translations: 77.8% compile errors, 13.4% functional, 8.4% runtime, 0.4% non-terminating.
Python-as-source worst for data bugs (→C 43%). Dynamic→static harder than reverse. Real-world
code shifts mix toward model constraints (29.4%) and removed logic (15.7%); adds mutability
contracts, overloading, decorators. Oracle = compile+run+existing tests; r=0.64–0.85 between
tests-per-sample and detected failures (weak-oracle evidence). No TS/JS, no Rust-as-LLM-target,
no unicode/recursion/statefulness axes (stdin-batch benchmarks). 2023-era models — taxonomy
durable, magnitudes stale.

### security-centric-translation (Chang et al., 2025; 720 samples, 9 CWEs, 5 LLMs)
VIR (patched→vulnerable) avg 36.9% (28.6–45%); vuln-preserved 65.4%. Taxonomy: input
validation 34.9% ("validation equivalence fallacy" — structure preserved, semantics lost),
security API/library misuse 32.7%, output encoding 17.8%, memory 10.9% (but 77% of CWE-416).
C/C++→Rust *best* pair (VIR 18.2%; 0% when output stayed in safe Rust). Detection: humans 49.6%
(~chance), SAST all <60 F1 (CodeQL recall 29.2%), multi-LLM judge 82.6 F1 best. Fuzzing NOT
evaluated (dismissed as impractical). RAG over vuln reports cut VIR ~33% at 12–15% correctness
cost. Implication: security gate should be differential-testing-with-adversarial-inputs first,
SAST second, LLM judge advisory.

## Verdict on the HANDOFF hypothesis

> "differential equivalence-checking of LLM ports is proven but has no clean open-source tool
> — that's the gap to fill"

**Confirmed, and understated.** The gap is not one missing tool but four missing properties:
language-agnostic (vs RustAssure's LLVM lock-in), stateful (vs universal single-call testing),
maintenance-oriented (vs universal one-shot framing), and measurable (vs universal
benchmark-test-suite oracles). No paper has more than one of these; none has the N-way peer
architecture at all.
