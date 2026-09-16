# Handoff: port-to-port similarity heatmap fixes — done

Six items plus a follow-up fix, one commit each, plus two blog commits. Nothing is outstanding.

| Item | Commit | What changed |
| --- | --- | --- |
| 1. Drop the empty row and column | `f247fe5` | x domain `items[1:]`, y domain `items[:-1]` |
| 2. Label the reference | `b49f125` | `REFERENCE_TICK = "reference"`; strips are conditions-only |
| 3. Print the reference values | `92626d6` | two text layers, ink/surface split at the ramp midpoint |
| 4. Spread the scale | `7a5834e` | fixed `[25, 85]` + `clamp`, legend ticks 25/50/75/85 |
| 5. Label size | `4930d24` | `MATRIX_LABEL_PX = 13`, refit to 757px |
| 6. Dark ramp floor | `6309b75` | `DARK_BLUE_RAMP` opens at `#2d5a8e` |
| 7. Dark ramp direction | `94da612` | five stops, monotonic to a pale top |
| 8. Values everywhere, wider ramps | `34df6bb` | every cell prints; both ramps gain range at the ends |

Blog: `thekevinscott.com` `af44427`, `231f32c` and `901f322` on `ks/picker-libre-franklin`.

## The blog downscale, which governs every font size here

The figure is fitted to a 757px slot, but the article's text column is 637.6px and
`img { max-width: 100% }`, so the SVG arrives at 0.84 scale. An SVG pixel is *not* a
page pixel. Widening the chart's natural width makes the text **smaller**, not larger —
the column is the cap either way, so a wider natural width simply scales down further.
The only levers are font size, or a markup change to break the figure out of the
column, which would mean editing `index.md` and is not ours to make. Value text is
therefore 11px in the SVG to land at 9.3px on the page;
`test_matrix_value_text_survives_the_blog_downscale` pins that relationship.

## Item 7, the one that came back

Item 6 lifted the floor but left the stop order alone, and the order was wrong. The
dark ramp was `SEQUENTIAL_BLUE`'s colours in `SEQUENTIAL_BLUE`'s order, but the two
ramps run opposite ways: on white the most similar pair is the *darkest* cell, on a
dark page it has to be the *brightest*. So the top stop `#256abf` (luminance 97.5) sat
below `#3987e5` (125.2) beneath it — cells above ~75 rendered duller than cells at 70,
the closest pairs read as dark specks, and the legend bar dimmed at its top edge.
Dropping the two darkest stops in item 6 shrank the end-to-end span from 257 to 13,
which is what made it obvious.

Now `["#2d5a8e", "#3a7fc4", "#5c9be0", "#8fbdf0", "#c5ddf8"]`: five stops matching
`SEQUENTIAL_BLUE`'s count, monotonic, span 134. Two tests guard it —
`test_dark_ramp_climbs_all_the_way_to_its_top` and
`test_dark_ramp_matches_the_light_ramp_stop_count`, the latter reading the light range
off the committed JSON rather than hardcoding 5.

**Known weak spot, now spread across the whole chart.** A monotonic ramp puts mid-range
values at mid luminance, where neither text colour has much contrast, and item 8 prints
a number in all 210 cells rather than 20. Cells either side of the 55 threshold are the
weakest; the ends of the ramp are comfortable. Widening both ramps in item 8 helped,
because more of the domain now sits away from the middle. Fixing the midtones properly
means a text halo or a per-cell colour choice, neither of which has been asked for.

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
