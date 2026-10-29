<div class="eyebrow">APPENDIX · HELD-OUT TESTS · WHAT "NOT LOADED" AND "LOADED, FAILING" MEAN</div>

# Three mechanisms, all at the interface

<table class="nb-table small">
<thead><tr><th>status</th><th>direction</th><th>what the driver saw</th><th>ports</th><th>by model</th></tr></thead>
<tr><td>not loaded</td><td>TypeScript → Python</td><td><code>cannot import name 'RuleEnd'</code></td><td>54</td><td>Sonnet 31, Opus 18, Haiku 5</td></tr>
<tr><td>not loaded</td><td>TypeScript → Python</td><td><code>No module named 'gbnf'</code></td><td>48</td><td>Haiku 41, Fable 6, Opus 1</td></tr>
<tr><td>not loaded</td><td>Python → TypeScript</td><td>no <code>src/index.ts</code></td><td>86</td><td>Sonnet 33, Haiku 30, Opus 23</td></tr>
<tr><td>loaded, failing</td><td>TypeScript → Python</td><td>every input raises</td><td>58</td><td>Fable 41, Sonnet 9, Opus 6, Haiku 2</td></tr>
<tr><td>loaded, failing</td><td>TypeScript → Python</td><td>mixed</td><td>2</td><td>Haiku 2</td></tr>
<tr><td>loaded, failing</td><td>Python → TypeScript</td><td>every input raises</td><td>58</td><td>Haiku 26, Fable 19, Sonnet 10, Opus 3</td></tr>
<tr><td>loaded, failing</td><td>Python → TypeScript</td><td>rejects every input</td><td>5</td><td>Opus 3, Sonnet 1, Fable 1</td></tr>
</table>
<table class="nb-table small" style="margin-top:10px;width:auto">
<thead><tr><th>driven ports</th><th>n</th><th>at the reference-bug ceiling</th><th>below it</th></tr></thead>
<tr><td>Fable</td><td>38</td><td>38</td><td>–</td></tr>
<tr><td>Opus</td><td>49</td><td>44</td><td>3 at 86.1%, 2 at 96.9%</td></tr>
<tr><td>Sonnet</td><td>15</td><td>12</td><td>3 at 86.1%</td></tr>
<tr><td>Haiku</td><td>0</td><td>0</td><td>–</td></tr>
</table>

<div class="nb-note">The driver imports <code>gbnf</code>, calls <code>GBNF(grammar, input)</code> and iterates for <code>RuleEnd</code>; in TypeScript it imports the default export of <code>src/index.ts</code>. A package nested under <code>python/</code> or <code>src/</code>, a renamed <code>RuleEnd</code>, or a class export that needs <code>new</code> scores 0 with no grammar parsed. Fable's Python ports define <code>RuleEnd</code> as a <code>TypedDict</code>, so the driver's <code>isinstance</code> raises on every accepted input. Ceiling = 97.5 % (779 / 799) and 99.4 % (794 / 799); the rest are the target reference's own bugs.</div>

<div class="source">v2-models-effort · drivers in <code>analysis/measure-behavior/drivers/</code> · 86.1 % = the same 106-pair over-accept set seen in the tests experiment; 96.9 % = the Python reference's IndexError carried into TypeScript · 2026-10-29</div>
