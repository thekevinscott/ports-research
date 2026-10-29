<div class="eyebrow">TAKEAWAY 2 · THE AGENT HAS A HOUSE STYLE. YOUR PORT IS THE OUTLIER.</div>

# Ports agree with each other more than with the handwritten port

<div class="finding-line"><strong>66 % vs 38 %</strong><span>Python → TypeScript: median line similarity between two ports of the same model and effort, versus between a port and the handwritten reference. Reference scores are layout-corrected: ports that put the package in a different folder were moved before scoring.</span></div>
<div class="finding-line"><strong>61 % vs 33 %</strong><span>TypeScript → Python: the same two numbers.</span></div>
<div class="finding-line"><strong>30 of 32</strong><span>model × effort × direction cells where the port-to-port median beats every port's score against the reference. The two exceptions (Opus low TypeScript → Python, Sonnet medium Python → TypeScript) are cells whose ports split between two package layouts, which drags the port-to-port score down as well.</span></div>

<div class="study-line">Run the port again and you get roughly the same code back. Compare it to the hand-written one and you do not. Whatever the agent's style is, it is consistent, and it is not yours.</div>

<div class="source">v2-models-effort · port-to-port: 66 pairs per cell among 12 ports, median of cell medians, <code>public/models-effort-pairs.json</code> · port-to-reference: <code>reference_diff_similarity_pct</code> in <code>public/models-effort-runs.csv</code>, overridden by <code>public/layout-corrected.csv</code> where a port was relocated · 2026-10-29</div>
