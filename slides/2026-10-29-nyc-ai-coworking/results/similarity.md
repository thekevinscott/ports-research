<div class="eyebrow">RESULTS · SIMILARITY TO THE HANDWRITTEN REFERENCE</div>


<div class="explain">Both measures compare the port's text with the handwritten version in the target language, file by file, after auto-formatting. <b>Diff lines</b> = lines added + deleted in <code>git diff</code>; 0 = identical. <b>Lines shared %</b> = 2 × shared lines ÷ (reference lines + port lines); 100 = identical. Files are matched by path, so a port that puts the package in a different folder shares nothing and scores near 0. Not embeddings.</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" initial-measure="diff_lines_changed" :measures="['diff_lines_changed', 'reference_diff_similarity_pct']" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · <code>measure-code-distance git-diff</code> · 2026-10-29</div>
