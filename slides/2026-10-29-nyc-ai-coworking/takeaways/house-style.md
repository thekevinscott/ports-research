<div class="eyebrow">TAKEAWAY 2 · THE AGENT HAS A HOUSE STYLE. YOUR PORT IS THE OUTLIER.</div>

# Ports agree with each other more than with the handwritten port

<RunStrips compact src="/models-effort-runs.csv" by="model-effort" initial-measure="reference_diff_similarity_pct" :measures="['reference_diff_similarity_pct', 'embedding_distance']" one-direction />

<div class="study-line">Port to port, same model and effort: 66 % / 61 % of lines shared. Port to handwritten reference, layout-corrected: 38 % / 33 %.</div>

<div class="source">v2-models-effort · port-to-port: 66 pairs per cell among 12 ports, median of cell medians, <code>public/models-effort-pairs.json</code> · port-to-reference: <code>public/models-effort-runs.csv</code> with <code>public/layout-corrected.csv</code> where a port was relocated · 2026-10-29</div>
