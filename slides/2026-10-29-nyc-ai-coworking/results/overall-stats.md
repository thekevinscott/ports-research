<div class="eyebrow">RESULTS · OVERALL STATISTICS</div>

<div class="explain"><b>Wall time</b> = agent run, start to exit. <b>Tokens</b> = all the transcript billed, cache reads and writes included. <b>Cost</b> = Claude Code's own figure, list price. <b>Files</b>, <b>LOC</b> = the port's source, tests and build tooling left out; LOC skips blanks and comments. Dashed = the handwritten version in the target language.</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" :measures="['wall_minutes', 'total_tokens', 'cost_usd', 'file_count', 'loc']" reference="/reference.json" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · cost = Claude Code's reported total_cost_usd per run, list price · 2026-10-29</div>
