<div class="eyebrow">RESULTS · SPEED OF THE PORTED LIBRARY</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-ladder.csv', tests: '/tests-configuration-ladder.csv' }" initial-measure="ladder_ref_ratio" :measures="['ladder_ref_ratio']" :reference-line="1" />

<div class="source">tests experiment: 137 of 192 ports timed (89 py→ts, 48 ts→py; the rest would not load) · models × effort: ladder batch running since 15:35Z over the 92 ports the held-out driver could run · ladder = 22 cases, <code>analysis/exercise-api/cases/ladder.jsonl</code> · <code>scripts/ladder_metrics.py</code> · 2026-10-29</div>
