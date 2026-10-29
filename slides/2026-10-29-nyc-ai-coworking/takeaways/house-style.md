<div class="eyebrow">TAKEAWAY 2 · THE AGENT HAS A HOUSE STYLE. HANDWRITTEN IMPLEMENTATIONS ARE THE OUTLIER.</div>

# Ports agree with each other more than with the handwritten port

<table class="nb-table money pairs">
<thead><tr><th>distance between</th><th>Python → TypeScript</th><th>TypeScript → Python</th></tr></thead>
<tbody>
<tr><td>two ports, same model and effort</td><td class="hot">0.015</td><td class="hot">0.028</td></tr>
<tr><td>two ports, same model, different effort</td><td class="hot">0.017</td><td class="hot">0.034</td></tr>
<tr><td>two ports, different models</td><td class="hot">0.022</td><td class="hot">0.050</td></tr>
<tr><td>a port and the handwritten implementation</td><td>0.044</td><td>0.068</td></tr>
</tbody>
</table>

<div class="nb-note">Median embedding distance, lower = closer. Every pair of the 383 ports in a direction (18,145 / 18,336 pairs), and each port against the handwritten implementation (191 / 192 ports). Closest cross-model pair of models: Fable ↔ Opus at 0.018 (Python → TypeScript), Haiku ↔ Sonnet at 0.040 (TypeScript → Python).</div>

<div class="source">v2-models-effort · 4 models × 4 efforts, pooled · <code>measure-embedding</code> chamfer distance · <code>public/models-effort-embedding-pairs.json</code><span class="date">2026-10-29</span></div>
