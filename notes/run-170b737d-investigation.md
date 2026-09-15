# Run 170b737d — outlier investigation

Question: is run `20260909T151143Z_170b737d` — whose git-diff port-to-port similarity
scores are 4–16 against every other port while all other pairs cluster far higher — a
measurement artifact or a legitimately divergent port?

**Verdict: legitimately divergent port. Not a measurement artifact.** The low scores are a
true property of the port's text, produced by one identifiable stylistic decision. The run
itself is one of the strongest in the corpus by functional measures.

## 1. The run

| | |
|---|---|
| run id | `20260909T151143Z_170b737d` |
| direction | python → typescript (forward leg) |
| condition | `source-python_effort-high_model-claude-opus-5` — **no tests** (neither suite provided) |
| model / agent | `claude-opus-5`, effort high |
| window | started 2026-09-09T15:11:43Z, completed 15:33:39Z (~22 min, 118 turns, $17.72) |
| gbnf commit | `13f1aca495d11e160fffd68c4ba299a2415909d8` |
| status | `terminal_reason: completed`, `is_error: false` |
| reverse leg | `20260910T085124Z_7f672549` (typescript → python, both suites, same model) |

## 2. Test results — did it pass what its condition entitles it to?

- The forward condition is **no tests**: the harness mounted no suites, so there was nothing
  to pass at run time. The agent wrote its own 219-test suite (all passing) plus a
  differential parity suite that replays the Python reference over 41 grammars; per its
  report the recorded fixtures were byte-identical to the reference's.
- The **reverse leg passed 773 tests** under the reverse condition (both suites), and its
  reverse similarity to the Python reference is **59.77% — the highest reverse score in the
  corpus**. A broken port cannot produce that.
- Post-hoc adapted suites (from the exported charts, python→typescript "no tests" cell):
  unit pass rates are [46.6, 46.6, 46.6, 46.6, 100] and integration coverage 65–68%.
  Whatever drives the 46.6 plateau is shared by four of the five no-tests ports — 170b737d
  is not singled out by it. (The adapted suites could not be re-run in this environment;
  the derivation cache is absent.)
- Ladder: 19/19 rungs completed at 0.835× reference time — in family.

No evidence of "failed everything but still got scored."

## 3. What the agent produced

A complete, real port: 34 TypeScript source files covering the full module tree
(`GBNF.ts`, `grammar_graph/*`, `grammar_parser/*`, `rules_builder/*`, `utils/*`), plus its
own test suite. Not empty, not a stub, not the wrong language, not truncated.

## 4. The similarity computation for this run

Re-ran `measure-code-distance git-diff` for 170b737d vs b96078c6 with the analysis's
exclude set: **12.10% locally vs 12.18% banked**. The small delta is explained by prettier
being uninstallable in this environment (no network), so formatting normalization was
skipped here; it is not material. The right files were compared (34 files, tests excluded
as designed), against the right reference, with no path or encoding oddity. The banked
number is reproducible and correct.

### Root cause of the divergence

170b737d is the **only port that kept the Python reference's snake_case identifiers
verbatim** (`parse_space`, `given_range`, `__roots__`), mirrored the Python package layout
(`src/grammar_graph/…`, with `.ts` import specifiers), rather than adopting TypeScript
conventions. Every other port — including the three other "rebuilt the file layout" runs
(9a3e20fe, 31ac2789, 5b46f630) — uses camelCase identifiers, so their lines match each
other and the reference at 41–87%.

The git-diff measure is line-text Dice similarity. A systematic identifier-case difference
breaks nearly every line, and pushes per-file similarity below git's 50% rename threshold
(only 7 of 34 files rename-match against b96078c6; the rest count as wholesale
delete+add). Hence 4–16% against everything, despite the code being equivalent.

Independent corroboration that the port is *semantically* in family:

- Embedding chamfer distances for its pairs are 0.0206–0.0302 — per-port median 0.0283,
  the most distant port but the same order as the field (0.0104–0.0301). Distance to the
  reference: 0.0563, vs the field's 0.034–0.058. On the embedding measure it is the high
  end of normal, not an outlier.
- Its one high line-similarity pair, 31ac2789 at 49.2%, is the other port that used a
  snake_case file layout (though camelCase identifiers with snake_case aliases).

## 5. Effect on result 2 (ports more similar to each other than to the reference)

### git-diff similarity, python → typescript

All within-direction pairs (the matrix):

| | port-pair median | port/reference median | pairs closer than both references |
|---|---|---|---|
| with 170b737d | 69.35 | 40.98 | 173/190 |
| without 170b737d | 70.10 | 41.13 | 170/171 |

Within-cell (the notebook's per-condition summary), **no tests** cell — the only cell the
run touches:

| | port-pair median | port/reference median |
|---|---|---|
| with 170b737d | 47.46 | 7.12 |
| without 170b737d | 57.14 | 21.14 |

The other three cells are unchanged (source 68.88/40.56, target 78.84/43.42,
both 76.94/41.55).

### Embedding chamfer distance, python → typescript

| | port-pair median | port/reference median | pairs closer than both references |
|---|---|---|---|
| with 170b737d | 0.01712 | 0.04157 | 189/190 |
| without 170b737d | 0.01632 | 0.03978 | 170/171 |

(typescript→python is untouched — 170b737d does not appear in that direction: 0.04467 /
0.06562, 169/190, with or without.)

The headline claim is unchanged either way; under embeddings, all 19 of the run's pairs
satisfy the claim. On the git-diff measure the direction-level medians move by less than a
point. The no-tests cell moves most, and there 170b737d actually *widens* the gap the
article reports (its reference similarity, 1.19%, is the lowest in the corpus).

## Recommendation

**Include, with a footnote.** The run is a genuine, functional datapoint — the strongest
reverse leg in the corpus — and its divergence has a one-sentence mechanistic explanation
worth stating: under the no-tests condition nothing enforces target-language conventions,
and this run transliterated Python identifiers verbatim, which a line-based similarity
measures as distance even though the embedding measure and the round-trip both show a
faithful port. Excluding it would be cherry-picking a stylistic outlier; including it
silently invites the reader to ask exactly the question this note answers. No re-run of
the analysis is needed — the banked numbers are reproducible and correct.
