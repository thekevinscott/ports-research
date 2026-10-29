<div class="eyebrow">RESULTS · SPEED OF THE PORTED LIBRARY</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-ladder.csv', tests: '/tests-configuration-ladder.csv' }" initial-measure="ladder_ref_ratio" :measures="['ladder_ref_ratio']" :reference-line="1" />

<div class="source">tests experiment: 137 of 192 ports timed (89 py→ts, 48 ts→py; the rest would not load) · models × effort: 111 of 383 ports timed so far (65 py→ts, 46 ts→py; 174 would not load, the rest still running) · ladder = 22 cases, <code>analysis/exercise-api/cases/ladder.jsonl</code> · <code>scripts/ladder_metrics.py</code> · 2026-10-29</div>
