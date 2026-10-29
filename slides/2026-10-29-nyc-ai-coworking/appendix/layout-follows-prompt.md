<div class="eyebrow">APPENDIX · WHERE THE PORTS PUT THE PACKAGE</div>

# Layout follows the prompt

<table class="nb-table small">
<thead><tr><th>direction</th><th>top of the port</th><th>ports</th><th>by model</th></tr></thead>
<tr><td colspan="4" class="dim">models × effort · long prompt · 413 ports</td></tr>
<tr><td>TypeScript → Python</td><td><code>gbnf/</code> at the top (the reference layout)</td><td>154</td><td>Sonnet 50, Opus 48, Fable 47, Haiku 9</td></tr>
<tr><td>TypeScript → Python</td><td><code>python/…</code></td><td>35</td><td>Haiku 33, Fable 2</td></tr>
<tr><td>TypeScript → Python</td><td><code>src/…</code></td><td>13</td><td>Haiku 8, Fable 4, Opus 1</td></tr>
<tr><td>Python → TypeScript</td><td><code>src/index.ts</code> present</td><td>125</td><td>Fable 52, Opus 31, Haiku 26, Sonnet 16</td></tr>
<tr><td>Python → TypeScript</td><td>no <code>src/index.ts</code></td><td>86</td><td>Sonnet 33, Haiku 30, Opus 23</td></tr>
<tr><td colspan="4" class="dim">tests experiment · short prompt · Opus medium · 192 ports</td></tr>
<tr><td>TypeScript → Python</td><td><code>gbnf/</code> at the top (the reference layout)</td><td>83</td><td>of 96</td></tr>
<tr><td>TypeScript → Python</td><td><code>src/…</code> or other</td><td>13</td><td>of 96</td></tr>
<tr><td>Python → TypeScript</td><td><code>src/index.ts</code> present</td><td>89</td><td>of 96</td></tr>
<tr><td>Python → TypeScript</td><td>no <code>src/index.ts</code></td><td>7</td><td>of 96</td></tr>
</table>

<div class="nb-note">The reference lives at <code>/input/python/gbnf</code> and <code>/input/javascript/src</code>. Similarity and the held-out driver match paths against that layout, so a port that keeps the <code>python/</code> prefix, or puts the TypeScript under <code>gbnf/</code> instead of <code>src/</code>, scores near 0 before a line is compared. Haiku's 1–3 % TypeScript → Python similarity is this. The one cell both experiments share, Opus medium with unit + source tests: 6 of 12 Python → TypeScript ports lack <code>src/index.ts</code> under the long prompt, 0 of 12 under the short one. Part of "not loaded" on the held-out slide is the prompt, not the model.</div>

<div class="source">v2-models-effort · top-level directories of each <code>ported_implementation/</code><span class="date">2026-10-29</span></div>
