<div class="eyebrow">RESULTS · HELD-OUT TESTS · HOW OFTEN THE PORT AGREES WITH THE REFERENCE</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" initial-measure="behavior_agreement_pct" :measures="['behavior_agreement_pct', 'api_agreement_pct']" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · drivers in <code>analysis/measure-behavior/drivers/</code> · 2026-10-29</div>
