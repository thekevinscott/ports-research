<div class="eyebrow">RESULTS · OVERALL STATISTICS</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" :measures="['wall_minutes', 'total_tokens', 'cost_usd', 'file_count', 'loc']" reference="/reference.json" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · cost = transcript API calls at list rates, <code>scripts/cost_metrics.py</code> · 2026-10-29</div>
