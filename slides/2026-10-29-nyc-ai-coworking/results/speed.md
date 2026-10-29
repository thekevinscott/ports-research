<div class="eyebrow">RESULTS · SPEED OF THE PORTED LIBRARY</div>

<div class="explain">Port and reference parse the same 22-grammar ladder, up to JSON nested 8,192 deep. <b>Value</b> = port's median parse time ÷ reference's. Dashed line = same speed; left of it is faster than the hand-written code. Unloadable ports have no dot.</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-ladder.csv', tests: '/tests-configuration-ladder.csv' }" initial-measure="ladder_ref_ratio" :measures="['ladder_ref_ratio']" :reference-line="1" />

<div class="source">tests experiment: 137 of 192 ports timed (89 py→ts, 48 ts→py; the rest would not load) · models × effort: ladder batch running since 14:35Z, serial, ~1–1.5 min per port · ladder = 22 cases, <code>analysis/exercise-api/cases/ladder.jsonl</code> · <code>scripts/ladder_metrics.py</code> · 2026-10-29</div>
