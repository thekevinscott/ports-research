<div class="eyebrow">RESULTS · SIMILARITY TO THE HANDWRITTEN REFERENCE</div>


<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" initial-measure="embedding_distance" :measures="['embedding_distance', 'reference_diff_similarity_pct', 'diff_lines_changed']" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · <code>measure-code-distance git-diff</code> · <code>measure-embedding</code> · 2026-10-29</div>
