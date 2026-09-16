# Handoff: port-to-port similarity heatmap fixes — done

All six items shipped, one commit each, plus a blog commit. Nothing is outstanding.

| Item | Commit | What changed |
| --- | --- | --- |
| 1. Drop the empty row and column | `f247fe5` | x domain `items[1:]`, y domain `items[:-1]` |
| 2. Label the reference | `b49f125` | `REFERENCE_TICK = "reference"`; strips are conditions-only |
| 3. Print the reference values | `92626d6` | two text layers, ink/surface split at the ramp midpoint |
| 4. Spread the scale | `7a5834e` | fixed `[25, 85]` + `clamp`, legend ticks 25/50/75/85 |
| 5. Label size | `4930d24` | `MATRIX_LABEL_PX = 13`, refit to 757px |
| 6. Dark ramp floor | `6309b75` | `DARK_BLUE_RAMP` opens at `#2d5a8e` |

Blog: `thekevinscott.com` `af44427` on `ks/picker-libre-franklin` (4 SVGs + 2 unused PNGs).

## Acceptance, checked on 1100px-viewport screenshots

Screenshots in `/tmp/claude/heat-{light,dark}-chart{,-tp}.png`; charts render at 637.6px.

- "reference" reads on the x axis, bold and inked, in both modes — yes.
- The reference column's numbers read in both modes — yes.
- No blank boxed row or column — yes.
- The 170b737d row separates from the undrawn triangle in dark mode — yes, it is a
  distinct floor-blue band against black.
- "The reference column is visibly lighter than its neighbours in BOTH modes" — **half
  true, and the wording is wrong for dark mode.** The reference values (medians 41 and
  33) sit near the ramp's floor. On the light page the floor is pale, so the column is
  lighter. On the dark page the floor is the darkest blue, so the column is *darker*.
  It is unmistakably separated from its neighbours either way, which is the point;
  making it literally lighter in dark mode would mean inverting the ramp, which would
  break the shared reading of colour across the two themes.

## Notes for whoever touches this next

`export_charts.py` still cannot run here — the notebook shells out to
`execute-test-suite`, `measure-embedding` and `measure-code-distance`, none of which
have their inputs. Each item was therefore made twice: in `runs.py` (source of truth)
and as a patch over the committed chart JSONs, then `fit_pair(specs, 757)` and
`write_chart(spec, path.with_suffix(""))`. The patch harness is disposable and was not
kept. If you regenerate from the notebook, diff the result against the committed JSONs
before trusting it.

Two data-shaped facts the code now depends on:

- Every reference-column value is below the ramp's midpoint, so the surface-coloured
  text layer is empty and is left out of the spec entirely. If that ever changes, the
  builder emits it and `test_matrix_prints_the_reference_columns_values_only` covers it.
- The fixed domain separates the port-to-port and port-to-reference medians by ~1.9 ramp
  stops, against ~1.35 for a domain fitted to the data. The original brief asked for
  "at least two"; 1.9 is what a `[25, 85]` domain actually yields.

Tests: `just test-unit` in `analysis/` (166 pass). `uv run marimo check runs.py` is clean.
Running anything with `uv` here rewrites `uv.lock`; that churn is unrelated and was
reverted.

## Hard rules that still apply

- NEVER modify the gbnf source (either language) — it is experiment input.
- Never bare `pytest` at a package root.
- Do not change the data, ordering, condition colours, or the title.
