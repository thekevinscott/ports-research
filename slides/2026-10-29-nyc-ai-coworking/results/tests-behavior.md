<div class="eyebrow">RESULTS · HELD-OUT TESTS · HOW OFTEN THE PORT AGREES WITH THE REFERENCE</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" initial-measure="behavior_agreement_pct" :measures="['behavior_agreement_pct', 'api_agreement_pct']" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · drivers in <code>analysis/measure-behavior/drivers/</code><span class="date">2026-10-29</span></div>

<!--
- Better models at higher effort produced ports that passed more often. Opus at low/medium: 0–5%; at high/very high: 91–97%. Sonnet only moves off zero at very high. Fable beats Sonnet at every effort.
- Unit and source tests were actively harmful. Target tests restored what they broke, but no tests scored the same as target tests (97–99%).
-->
