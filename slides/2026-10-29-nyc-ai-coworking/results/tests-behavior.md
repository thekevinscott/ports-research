<div class="eyebrow">RESULTS · HELD-OUT TESTS · HOW OFTEN THE PORT AGREES WITH THE REFERENCE</div>

<RunStrips src="/models-effort-runs.csv" by="model-effort" initial-measure="behavior_agreement_pct" :measures="['behavior_agreement_pct', 'api_agreement_pct']" />

<div class="source">v2-models-effort · n=12 per cell and direction · behaviour = % of held-out grammars where the port accepts and rejects the same inputs as the handwritten reference · API = % of held-out calls where the port returns the same value as the reference · 2026-10-29</div>
