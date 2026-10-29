<div class="eyebrow">RESULTS · SPEED OF THE PORTED LIBRARY</div>

<div class="explain">Port and handwritten reference parse the same ladder of grammars, from a one-character literal to JSON nested 8,192 deep. <b>Value</b> = port's median parse time ÷ reference's. 1 = same speed; lower is faster than the hand-written code. Ports the driver could not load have no dot.</div>

<div class="speed-pair">
  <div>
    <div class="prompt-label">Tests experiment · Opus medium · by tests seen</div>
    <MeasurePanels src="/tests-configuration-ladder.csv" by="condition" :measures="['ladder_ref_ratio']" :reference-line="1" :width="360" :height="122" />
  </div>
  <div>
    <div class="prompt-label">Models × effort · batch in progress</div>
    <RunStrips src="/models-effort-ladder.csv" by="model-effort" initial-measure="ladder_ref_ratio" :measures="['ladder_ref_ratio']" />
  </div>
</div>

<div class="source">v2-tests-configuration: 137 of 192 ports timed (89 py→ts, 48 ts→py; the rest would not load) · v2-models-effort: ladder batch running since 14:35Z, serial, ~1–1.5 min per port · ladder = 22 cases, <code>analysis/exercise-api/cases/ladder.jsonl</code> · <code>scripts/ladder_metrics.py</code> · 2026-10-29</div>
