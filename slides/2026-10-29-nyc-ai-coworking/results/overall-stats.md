<div class="eyebrow">RESULTS · OVERALL STATISTICS</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" :measures="['wall_minutes', 'total_tokens', 'cost_usd', 'file_count', 'loc']" reference="/reference.json" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · cost = transcript API calls at list rates, <code>scripts/cost_metrics.py</code> · 2026-10-29</div>

<!--
- Wall time: effort matters
- Haiku uses more tokens but cost depends on models
- Files & LOC: all ports were smaller than the references
- Tests
  - Unit tests increased cost (2.5–3.3M tokens vs 0.8–1.6M). Likely because the port carried the unit tests too; not measured.
  - Integration tests were cheaper than no tests at all.
-->
