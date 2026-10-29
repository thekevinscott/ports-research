<div class="eyebrow">APPENDIX · HELD-OUT TESTS · WHEN A PORT SCORES 0, WHAT FAILED?</div>

<table class="nb-table small status-grid">
<thead><tr><th>model</th><th>effort</th><th colspan="3">Python → TypeScript</th><th colspan="3">TypeScript → Python</th></tr>
<tr><th></th><th></th><th>not loaded</th><th>loaded, failing</th><th>driven</th><th>not loaded</th><th>loaded, failing</th><th>driven</th></tr></thead>
<tr><td>Fable</td><td>low</td><td class="dim">0</td><td class="dim">8</td><td class="">4 / 12</td><td class="dim">0</td><td class="dim">12</td><td class="">0 / 12</td></tr>
<tr><td>Fable</td><td>medium</td><td class="dim">0</td><td class="dim">7</td><td class="">5 / 12</td><td class="dim">1</td><td class="dim">10</td><td class="">1 / 12</td></tr>
<tr><td>Fable</td><td>high</td><td class="dim">0</td><td class="dim">1</td><td class="hot">11 / 12</td><td class="dim">0</td><td class="dim">10</td><td class="">2 / 12</td></tr>
<tr><td>Fable</td><td>very high</td><td class="dim">0</td><td class="dim">4</td><td class="hot">8 / 12</td><td class="dim">5</td><td class="dim">5</td><td class="">2 / 12</td></tr>
<tr><td>Opus</td><td>low</td><td class="dim">2</td><td class="dim">3</td><td class="hot">7 / 12</td><td class="dim">12</td><td class="dim">0</td><td class="">0 / 12</td></tr>
<tr><td>Opus</td><td>medium</td><td class="dim">6</td><td class="dim">2</td><td class="">4 / 12</td><td class="dim">6</td><td class="dim">2</td><td class="">4 / 12</td></tr>
<tr><td>Opus</td><td>high</td><td class="dim">6</td><td class="dim">1</td><td class="">5 / 12</td><td class="dim">1</td><td class="dim">2</td><td class="hot">9 / 12</td></tr>
<tr><td>Opus</td><td>very high</td><td class="dim">6</td><td class="dim">0</td><td class="hot">6 / 12</td><td class="dim">0</td><td class="dim">1</td><td class="hot">11 / 12</td></tr>
<tr><td>Sonnet</td><td>low</td><td class="dim">8</td><td class="dim">4</td><td class="">0 / 12</td><td class="dim">12</td><td class="dim">0</td><td class="">0 / 12</td></tr>
<tr><td>Sonnet</td><td>medium</td><td class="dim">6</td><td class="dim">5</td><td class="">1 / 12</td><td class="dim">12</td><td class="dim">0</td><td class="">0 / 12</td></tr>
<tr><td>Sonnet</td><td>high</td><td class="dim">10</td><td class="dim">2</td><td class="">0 / 12</td><td class="dim">7</td><td class="dim">2</td><td class="">3 / 12</td></tr>
<tr><td>Sonnet</td><td>very high</td><td class="dim">8</td><td class="dim">0</td><td class="">4 / 12</td><td class="dim">0</td><td class="dim">7</td><td class="">5 / 12</td></tr>
<tr><td>Haiku</td><td>low</td><td class="dim">3</td><td class="dim">9</td><td class="">0 / 12</td><td class="dim">12</td><td class="dim">0</td><td class="">0 / 12</td></tr>
<tr><td>Haiku</td><td>medium</td><td class="dim">11</td><td class="dim">1</td><td class="">0 / 12</td><td class="dim">12</td><td class="dim">0</td><td class="">0 / 12</td></tr>
<tr><td>Haiku</td><td>high</td><td class="dim">6</td><td class="dim">6</td><td class="">0 / 12</td><td class="dim">12</td><td class="dim">0</td><td class="">0 / 12</td></tr>
<tr><td>Haiku</td><td>very high</td><td class="dim">3</td><td class="dim">8</td><td class="">0 / 11</td><td class="dim">9</td><td class="dim">3</td><td class="">0 / 12</td></tr>
</table>

<div class="nb-note">Over 413 runs: 102 driven · 123 loaded but failing · 188 not loaded. Driven by effort, both directions pooled (n = 96 each, 95 for very high): low 11 · medium 15 · high 30 · very high 36. The behaviour and API slide plots every run. A 0 is a port the driver could not run. A loaded port that accepted nothing the reference accepts lands on a floor: 39.8 % TypeScript → Python (60 ports), 9.6 % Python → TypeScript (58 ports). The 39.8 median on that slide is this floor, not partial correctness.</div>

<div class="source">v2-models-effort · max runs on their own slide · <code>public/models-effort-status.csv</code> from <code>scripts/status_metrics.py</code> · not loaded = every held-out pair crashed · loaded, failing = the port accepted none of the inputs the reference accepts · driven = otherwise · 2026-10-29</div>
