<div class="eyebrow">RESULTS · SPEED OF THE PORTED LIBRARY</div>

<div class="explain">Port and reference parse the same 22-grammar ladder, up to JSON nested 8,192 deep. <b>Value</b> = port's median parse time ÷ reference's. Dashed line = same speed; left of it is faster than the hand-written code. Unloadable ports have no dot.</div>

<div class="speed-pair">
  <div>
    <div class="prompt-label">Tests experiment · Opus medium · by tests seen</div>
    <RunStrips src="/tests-configuration-ladder.csv" by="condition" initial-measure="ladder_ref_ratio" :measures="['ladder_ref_ratio']" :reference-line="1" />
  </div>
  <div>
    <div class="prompt-label">Models × effort · batch in progress</div>
    <RunStrips src="/models-effort-ladder.csv" by="model-effort" initial-measure="ladder_ref_ratio" :measures="['ladder_ref_ratio']" :reference-line="1" />
  </div>
</div>

<div class="source">v2-tests-configuration: 137 of 192 ports timed (89 py→ts, 48 ts→py; the rest would not load) · v2-models-effort: ladder batch running since 14:35Z, serial, ~1–1.5 min per port · ladder = 22 cases, <code>analysis/exercise-api/cases/ladder.jsonl</code> · <code>scripts/ladder_metrics.py</code> · 2026-10-29</div>
