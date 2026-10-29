<div class="eyebrow">TAKEAWAY 2 · THE AGENT HAS A HOUSE STYLE. HANDWRITTEN IMPLEMENTATIONS ARE THE OUTLIER.</div>

# Ports agree with each other more than with the handwritten port

<table class="nb-table money pairs">
<thead><tr><th>model</th><th colspan="2">Python → TypeScript</th><th colspan="2">TypeScript → Python</th></tr>
<tr><th></th><th>port ↔ port</th><th>port ↔ handwritten</th><th>port ↔ port</th><th>port ↔ handwritten</th></tr></thead>
<tbody>
<tr><td>Fable</td><td class="hot">0.010</td><td>0.036</td><td class="hot">0.025</td><td>0.070</td></tr>
<tr><td>Opus</td><td class="hot">0.016</td><td>0.044</td><td class="hot">0.042</td><td>0.072</td></tr>
<tr><td>Sonnet</td><td class="hot">0.016</td><td>0.047</td><td class="hot">0.026</td><td>0.066</td></tr>
<tr><td>Haiku</td><td class="hot">0.017</td><td>0.047</td><td class="hot">0.027</td><td>0.062</td></tr>
</tbody>
</table>

<div class="nb-note">Median embedding distance, lower = closer. port ↔ port: every pair of ports from the same model and effort (264 pairs per model and direction). port ↔ handwritten: each port against the handwritten implementation (48 per model and direction).</div>

<div class="source">v2-models-effort · all four efforts pooled · <code>measure-embedding</code> chamfer distance · <code>public/models-effort-embedding-pairs.json</code> · 2026-10-29</div>
