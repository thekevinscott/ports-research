<div class="eyebrow">RESULTS · SIMILARITY TO THE HANDWRITTEN REFERENCE</div>


<RunStrips :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" initial-measure="diff_lines_changed" :measures="['diff_lines_changed', 'reference_diff_similarity_pct']" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · diff lines = lines added + deleted in <code>git diff</code> between port and handwritten reference, both auto-formatted; 0 = identical · similarity % = shared lines ÷ all lines, files matched by path; 100 = identical · 2026-10-29</div>
