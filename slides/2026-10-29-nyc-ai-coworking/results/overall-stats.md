<div class="eyebrow">RESULTS · OVERALL STATISTICS</div>

<div class="explain"><b>Wall time</b> = the agent run, start to exit. <b>Tokens</b> = every token the transcript billed: input, output, cache writes and cache reads. <b>Cost</b> = Claude Code's own figure, list price. <b>Files</b> and <b>LOC</b> = the port's source files, tests and build tooling left out; LOC counts code lines, not blanks or comments. Dashed = the handwritten version in the target language.</div>

<RunStrips :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" :measures="['wall_minutes', 'total_tokens', 'cost_usd', 'file_count', 'loc']" reference="/reference.json" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · cost = Claude Code's reported total_cost_usd per run, list price · 2026-10-29</div>
