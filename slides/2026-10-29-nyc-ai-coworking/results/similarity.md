<div class="eyebrow">RESULTS · SIMILARITY TO THE HANDWRITTEN REFERENCE</div>


<div class="explain">All three compare the port with the handwritten version in the target language, file by file. <b>Diff lines</b> = lines added + deleted in <code>git diff</code> after auto-formatting; 0 = identical. <b>Lines shared %</b> = 2 × shared ÷ (reference + port lines); 100 = identical. Both match files by path, so a relocated package scores near 0 (takeaway 2 corrects that). <b>Embedding distance</b> = per-file embeddings (qwen3-embedding-0.6b), each file to its nearest on the other side, averaged both ways; 0 = identical.</div>

<RunStrips compact :sources="{ 'models-effort': '/models-effort-runs.csv', tests: '/tests-configuration-runs.csv' }" initial-measure="diff_lines_changed" :measures="['diff_lines_changed', 'reference_diff_similarity_pct', 'embedding_distance']" />

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · n=12 per cell and direction · <code>measure-code-distance git-diff</code> · <code>measure-embedding</code> · 2026-10-29</div>
