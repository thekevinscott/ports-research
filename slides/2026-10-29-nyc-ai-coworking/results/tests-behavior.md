<div class="eyebrow">RESULTS · HELD-OUT TESTS · HOW OFTEN THE PORT AGREES WITH THE REFERENCE</div>

<div class="explain">Grammars and parser calls the agent never saw, run through the port and the handwritten version in the target language side by side. <b>Behaviour</b> = share of held-out grammars where both accept and reject the same input strings. <b>API</b> = share of held-out calls where both return the same value. 100 = indistinguishable on these inputs; a port the driver cannot load scores 0.</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" initial-measure="behavior_agreement_pct" :measures="['behavior_agreement_pct', 'api_agreement_pct']" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · drivers in <code>analysis/measure-behavior/drivers/</code> · 2026-10-29</div>
