<div class="eyebrow">RESULTS · OVERALL STATISTICS</div>

<div class="explain"><b>Wall time</b> = agent run, start to exit. <b>Tokens</b> = all the transcript billed, cache reads and writes included. <b>Cost</b> = every API call in the transcript priced at Claude API list rates. <b>Files</b>, <b>LOC</b> = the port's source, tests and build tooling left out; LOC skips blanks and comments. Dashed = the handwritten version in the target language.</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" :measures="['wall_minutes', 'total_tokens', 'cost_usd', 'file_count', 'loc']" reference="/reference.json" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · cost = transcript API calls at list rates, <code>scripts/cost_metrics.py</code> · 2026-10-29</div>
