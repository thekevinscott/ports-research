<div class="eyebrow">BACKUP · HELD-OUT TESTS · WHEN A PORT SCORES 0, WHAT FAILED?</div>

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


---

<div class="eyebrow">BACKUP · HELD-OUT TESTS · WHAT "NOT LOADED" AND "LOADED, FAILING" MEAN</div>

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


---


<div class="eyebrow">BACKUP · SAME MODEL, SAME EFFORT, SAME TESTS, TWO EXPERIMENTS</div>

# Opus medium with unit + source tests: the prompt is the only known difference

<table class="nb-table small">
<thead><tr><th>cell</th><th>n</th><th>wall min</th><th>tokens</th><th>cost $</th><th>files</th><th>LOC</th><th>diff lines</th><th>similarity %</th><th>behaviour %</th><th>API %</th><th>driven</th></tr></thead>
<tr><td>Python → TypeScript · models × effort (long prompt)</td><td>12</td><td>8.5</td><td>3,230,318</td><td>3.06</td><td>37.0</td><td>1,016.5</td><td>2,185.5</td><td>25.4</td><td>4.8</td><td>0.0</td><td>4</td></tr>
<tr><td>Python → TypeScript · tests experiment (short prompt)</td><td>12</td><td>8.4</td><td>3,236,538</td><td>2.79</td><td>37.0</td><td>1,012.0</td><td>1,727.0</td><td>40.7</td><td>97.5</td><td>87.8</td><td>8</td></tr>
<tr><td>TypeScript → Python · models × effort (long prompt)</td><td>12</td><td>7.7</td><td>3,119,000</td><td>2.64</td><td>37.0</td><td>1,025.5</td><td>2,065.5</td><td>32.8</td><td>19.9</td><td>9.0</td><td>4</td></tr>
<tr><td>TypeScript → Python · tests experiment (short prompt)</td><td>12</td><td>8.4</td><td>3,287,713</td><td>2.85</td><td>36.0</td><td>956.5</td><td>1,984.5</td><td>33.0</td><td>39.8</td><td>9.0</td><td>10</td></tr>
</table>

<div class="nb-note">Medians. Size, time and tokens agree across the two experiments; diff lines and the held-out scores do not. The models × effort runs got the longer prompt (reference marked read-only, both Dockerfiles pasted in). "Driven" for the tests experiment counts ports with both held-out scores above 0. Twelve runs per cell: this is one cell, not a replication study.</div>

<div class="source">v2-models-effort vs v2-tests-configuration · Opus = claude-opus-5-5 · unit + source = the reference's unit tests plus the language-agnostic integration tests in the source language · 2026-10-29</div>


---

<div class="eyebrow">BACKUP · THE MAX RUNS · HIDDEN FROM THE CHARTS</div>

# max against very high: 30 runs so far, 1 to 9 per cell

<table class="nb-table small">
<thead><tr><th>direction</th><th>model</th><th>effort</th><th>n</th><th>wall min</th><th>tokens</th><th>cost $</th><th>LOC</th><th>diff lines</th><th>behaviour %</th><th>API %</th><th>driven</th></tr></thead>
<tr><td>Python → TypeScript</td><td>Fable</td><td>very high</td><td>12</td><td>31.3</td><td>5,205,744</td><td>14.36</td><td>1,036</td><td>1,676</td><td>97.5</td><td>89.7</td><td>8 / 12</td></tr>
<tr><td>Python → TypeScript</td><td>Fable</td><td>max</td><td>4</td><td>51.2</td><td>4,349,127</td><td>17.35</td><td>1,022</td><td>1,698</td><td>97.5</td><td>89.7</td><td>4 / 4</td></tr>
<tr><td>Python → TypeScript</td><td>Opus</td><td>very high</td><td>12</td><td>29.2</td><td>11,234,867</td><td>8.63</td><td>1,113</td><td>2,282</td><td>48.7</td><td>43.9</td><td>6 / 12</td></tr>
<tr><td>Python → TypeScript</td><td>Opus</td><td>max</td><td>6</td><td>80.7</td><td>34,634,241</td><td>24.57</td><td>1,058</td><td>2,470</td><td>48.7</td><td>43.9</td><td>3 / 6</td></tr>
<tr><td>Python → TypeScript</td><td>Sonnet</td><td>very high</td><td>12</td><td>21.2</td><td>10,325,860</td><td>3.65</td><td>1,062</td><td>2,857</td><td>0.0</td><td>0.0</td><td>4 / 12</td></tr>
<tr><td>Python → TypeScript</td><td>Sonnet</td><td>max</td><td>1</td><td>60.2</td><td>53,142,672</td><td>11.42</td><td>1,323</td><td>3,375</td><td>0.0</td><td>0.0</td><td>0 / 1</td></tr>
<tr><td>Python → TypeScript</td><td>Haiku</td><td>very high</td><td>11</td><td>18.8</td><td>15,810,158</td><td>1.49</td><td>1,013</td><td>1,816</td><td>9.6</td><td>0.0</td><td>0 / 11</td></tr>
<tr><td>Python → TypeScript</td><td>Haiku</td><td>max</td><td>9</td><td>28.4</td><td>30,016,627</td><td>2.71</td><td>1,042</td><td>2,642</td><td>0.0</td><td>0.0</td><td>0 / 9</td></tr>
<tr><td>TypeScript → Python</td><td>Fable</td><td>very high</td><td>12</td><td>27.8</td><td>5,196,706</td><td>13.10</td><td>1,070</td><td>2,191</td><td>39.8</td><td>9.0</td><td>2 / 12</td></tr>
<tr><td>TypeScript → Python</td><td>Fable</td><td>max</td><td>5</td><td>45.3</td><td>5,951,717</td><td>18.49</td><td>1,116</td><td>2,312</td><td>39.8</td><td>9.0</td><td>1 / 5</td></tr>
<tr><td>TypeScript → Python</td><td>Opus</td><td>very high</td><td>12</td><td>28.4</td><td>13,311,610</td><td>8.15</td><td>1,205</td><td>2,268</td><td>99.4</td><td>94.9</td><td>11 / 12</td></tr>
<tr><td>TypeScript → Python</td><td>Opus</td><td>max</td><td>1</td><td>83.9</td><td>28,038,511</td><td>14.88</td><td>1,192</td><td>2,358</td><td>39.8</td><td>9.9</td><td>0 / 1</td></tr>
<tr><td>TypeScript → Python</td><td>Sonnet</td><td>very high</td><td>12</td><td>28.6</td><td>12,013,940</td><td>3.71</td><td>1,144</td><td>2,198</td><td>39.8</td><td>9.0</td><td>5 / 12</td></tr>
<tr><td>TypeScript → Python</td><td>Sonnet</td><td>max</td><td>2</td><td>116.1</td><td>55,064,600</td><td>12.00</td><td>1,390</td><td>2,610</td><td>99.4</td><td>94.9</td><td>2 / 2</td></tr>
<tr><td>TypeScript → Python</td><td>Haiku</td><td>very high</td><td>12</td><td>20.1</td><td>16,866,758</td><td>1.64</td><td>970</td><td>2,940</td><td>0.0</td><td>0.0</td><td>0 / 12</td></tr>
<tr><td>TypeScript → Python</td><td>Haiku</td><td>max</td><td>2</td><td>50.7</td><td>46,758,099</td><td>5.82</td><td>1,045</td><td>2,637</td><td>19.9</td><td>4.5</td><td>0 / 2</td></tr>
</table>

<div class="nb-note">Medians over the runs that exist. max roughly doubles wall time and spend over very high for every model; it does not move size, diff lines or the held-out scores on this evidence. The charts hide max because its cells are 1 to 9 runs against 12 everywhere else.</div>

<div class="source">v2-models-effort · max runs banked through 2026-10-29 · 2026-10-29</div>


---

<div class="eyebrow">BACKUP · SIMILARITY AS A PERCENTAGE · AND WHY HAIKU SITS APART</div>

<RunStrips src="/models-effort-runs.csv" by="model-effort" initial-measure="reference_diff_similarity_pct" :measures="['reference_diff_similarity_pct', 'diff_lines_changed']" />

<div class="source">v2-models-effort · similarity % = 2 × shared lines ÷ (reference lines + port lines), after formatting, files matched by path · a port whose package sits under a different directory shares no paths and scores near 0 · 2026-10-29</div>

---

<div class="eyebrow">BACKUP · WHERE THE PORTS PUT THE PACKAGE</div>

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

<div class="source">v2-models-effort · top-level directories of each <code>ported_implementation/</code> · 2026-10-29</div>

---

<div class="eyebrow">BACKUP · WHAT THE STUDY TOOK</div>

<div class="nb-row wide">
<table class="nb-table small">
<thead><tr><th></th><th>runs</th><th>spend</th><th>tokens</th><th>agent time</th></tr></thead>
<tr class=""><td>models × effort (incl. 30 max)</td><td>413</td><td>$1,912</td><td>3,007 M</td><td>130 h</td></tr><tr class=""><td>&nbsp;&nbsp;Fable</td><td>105</td><td>$1,081</td><td>426 M</td><td>39 h</td></tr><tr class=""><td>&nbsp;&nbsp;Opus</td><td>103</td><td>$536</td><td>777 M</td><td>37 h</td></tr><tr class=""><td>&nbsp;&nbsp;Sonnet</td><td>99</td><td>$173</td><td>527 M</td><td>20 h</td></tr><tr class=""><td>&nbsp;&nbsp;Haiku</td><td>106</td><td>$122</td><td>1,277 M</td><td>34 h</td></tr>
<tr class=""><td>tests experiment (Opus medium)</td><td>192</td><td>$355</td><td>411 M</td><td>23 h</td></tr>
<tr class="hot"><td>both</td><td>605</td><td>$2,267</td><td>3,418 M</td><td>153 h</td></tr>
<tr><td colspan="5" class="dim">models × effort spend by what the held-out driver could do with the port</td></tr>
<tr class=""><td>&nbsp;&nbsp;driver ran the port</td><td>102</td><td>$804</td><td>782 M</td><td>46 h</td></tr><tr class=""><td>&nbsp;&nbsp;loaded, failing</td><td>123</td><td>$676</td><td>815 M</td><td>39 h</td></tr><tr class=""><td>&nbsp;&nbsp;not loaded</td><td>188</td><td>$432</td><td>1,410 M</td><td>46 h</td></tr>
</table>
<table class="nb-table small" style="width:auto">
<thead><tr><th>driven ports</th><th>Python → TypeScript</th><th>TypeScript → Python</th></tr></thead>
<tr><td>Fable</td><td>32 / 52</td><td>6 / 53</td></tr><tr><td>Opus</td><td>25 / 54</td><td>24 / 49</td></tr><tr><td>Sonnet</td><td>5 / 49</td><td>10 / 50</td></tr><tr><td>Haiku</td><td>0 / 56</td><td>0 / 50</td></tr>
</table>
</div>

<div class="nb-note">Spend is every API call in the transcripts priced at Claude API list rates, summed; tokens are input, output and cache reads and writes from the transcripts. Agent time is wall-clock inside the container, summed, not calendar time: batches ran in parallel over about two weeks. Haiku used the most tokens of any model and the least money.</div>

<div class="source">v2-models-effort (413 runs) and v2-tests-configuration (192 runs) · <code>public/models-effort-runs.csv</code>, <code>public/tests-configuration-runs.csv</code>, <code>public/models-effort-status.csv</code> · 2026-10-29</div>

---

<div class="eyebrow">BACKUP · THE PROMPT THE 413 MODEL × EFFORT RUNS GOT</div>

# The long prompt

<div class="prompt-layout">
<div class="prompt-col">
<pre class="prompt-text" style="font-size:10px;line-height:1.3;margin:0">You are porting software from one language to another.
The reference is mounted read-only at `/input`.
Write the port to `/target`.
There is no network access.
The sandbox image was built from these two Dockerfiles, the second on top of the first:
<span class="dim">[Dockerfile 1, 23 lines: node:24 base, Claude Code 2.1.296, socat, botbox-relay]</span>
<span class="dim">[Dockerfile 2, 20 lines: uv, Python 3.14.3, pytest, vitest, pnpm]</span>
The library itself may specify additional porting instructions below. Paths in them are relative to `/input`.
Port the implementation under python/ to typescript.
The following test suites are included:
- python unit tests: python/gbnf/ (colocated, *_test.py)
- python integration tests: python/tests/generated/</pre>
</div>
<div class="prompt-col">
<div class="prompt-label">Against the short one (slide 5)</div>
<ul class="prompt-notes">
<li>2,170 characters against about 450. The two Dockerfiles are 1,565 of them.</li>
<li>"mounted read-only" is new. The short prompt said only "mounted at /input".</li>
<li>"There is no network access" moved up; the tool list (uv, pytest, pnpm, vitest) left the prose for the Dockerfiles.</li>
<li>Two suites listed (unit, source integration) instead of one.</li>
<li>The Dockerfiles changed twice during the batch (botbox 0.0.20 → 0.1.1 → 0.1.72) and a memory cap was added; all three recorded in the experiment's DEVIATIONS.md.</li>
</ul>
</div>
</div>

<div class="source">Run 20261028-032612-bold-tooth (python → typescript), blank lines and Dockerfiles collapsed; full text in <code>public/long-prompt.txt</code> · 2026-10-29</div>

---

<div class="eyebrow">BACKUP · HELD-OUT TESTS · THE ONE NAME MOST TYPESCRIPT → PYTHON PORTS FAILED ON</div>

# Two shapes of <code>RuleEnd</code>, one driver per side

<div class="nb-row wide">
<pre class="prompt-text" style="margin:0;font-size:10.5px;line-height:1.35;white-space:pre"># Python reference
class RuleEnd(Rule): ...          # gbnf/__init__.py exports it
# Python driver
from gbnf import GBNF, RuleEnd
any(isinstance(rule, RuleEnd) for rule in state)</pre>
<pre class="prompt-text" style="margin:0;font-size:10.5px;line-height:1.35;white-space:pre">// TypeScript reference
export interface RuleEnd { type: RuleType.END }  // erased
// TypeScript driver
const { default: GBNF } = await import(src/index.ts)
state.some(rule => rule.type === "end")</pre>
</div>

<table class="nb-table small">
<thead><tr><th>how the TypeScript → Python port defines <code>RuleEnd</code></th><th>ports</th><th>driven</th><th>loaded, failing</th><th>not loaded</th><th>by model</th></tr></thead>
<tr><td><code>class RuleEnd(Rule)</code>, like the Python reference</td><td>28</td><td class="hot">28</td><td>0</td><td>0</td><td>21 Opus, 7 Sonnet</td></tr><tr><td>an alias (<code>RuleEnd = …</code>)</td><td>22</td><td class="hot">6</td><td>10</td><td>6</td><td>7 Sonnet, 6 Opus, 6 Fable, 3 Haiku</td></tr><tr><td><code>class RuleEnd(TypedDict)</code>, like the TypeScript interface</td><td>76</td><td class="">0</td><td>49</td><td>27</td><td>40 Fable, 26 Haiku, 7 Sonnet, 3 Opus</td></tr><tr><td>named, but not defined at top level</td><td>17</td><td class="hot">6</td><td>1</td><td>10</td><td>7 Fable, 4 Sonnet, 4 Opus, 2 Haiku</td></tr><tr><td>no <code>RuleEnd</code> anywhere</td><td>59</td><td class="">0</td><td>0</td><td>59</td><td>25 Sonnet, 19 Haiku, 15 Opus</td></tr>
</table>

<div class="nb-note">202 ports. Every port that wrote the class the Python reference has was driven. A <code>TypedDict</code> mirrors the TypeScript interface and fails the driver's <code>isinstance</code> on every accepted input (the 39.8 % floor) or at import. The TypeScript driver duck-types; it has no equivalent failure.</div>

<div class="source">v2-models-effort · <code>public/models-effort-ruleend.csv</code> from <code>scripts/ruleend_metrics.py</code> · drivers in <code>analysis/measure-behavior/drivers/</code> · 2026-10-29</div>

---

<div class="eyebrow">BACKUP · SIMILARITY ONCE THE PACKAGE IS MOVED TO WHERE THE REFERENCE KEEPS IT</div>

# Move the folder, fix the case, re-measure

<table class="nb-table small" style="width:auto">
<thead><tr><th>direction</th><th>model</th><th>misplaced ports</th><th>as scored</th><th>folder moved</th><th>also renamed</th><th>final</th></tr></thead>
<tr><td>TypeScript → Python</td><td>Fable</td><td>6</td><td>6.3</td><td>33.7</td><td>0</td><td class="hot">33.7</td></tr><tr><td>TypeScript → Python</td><td>Opus</td><td>1</td><td>0.3</td><td>32.1</td><td>0</td><td class="hot">32.1</td></tr><tr><td>TypeScript → Python</td><td>Haiku</td><td>41</td><td>1.3</td><td>34.5</td><td>0</td><td class="hot">34.5</td></tr><tr><td>Python → TypeScript</td><td>Opus</td><td>23</td><td>8.0</td><td>8.3</td><td>23</td><td class="hot">37.5</td></tr><tr><td>Python → TypeScript</td><td>Sonnet</td><td>33</td><td>1.2</td><td>1.3</td><td>33</td><td class="hot">27.0</td></tr><tr><td>Python → TypeScript</td><td>Haiku</td><td>30</td><td>8.7</td><td>36.3</td><td>6</td><td class="hot">37.4</td></tr></table>

<div class="nb-note">The 134 ports whose package is not where the reference keeps it, copied to scratch and re-scored with the same git-diff measure after two mechanical fixes, nothing inside any file changed. First the package directory is moved (<code>python/gbnf → gbnf</code>, <code>gbnf → src</code>, and so on). That alone lifts every TypeScript → Python port to 32–35 %. 62 Python → TypeScript ports (all Sonnet, all Opus, 6 Haiku) still match nothing because they name folders <code>rules_builder/</code> where the reference has <code>rules-builder/</code>; lower-casing and dashing those names lifts them to 27–38 %. Medians in the "final" column use the renamed score where a rename was applied. The lowest of the 134 after both fixes is 20.0 %.</div>

<div class="source">v2-models-effort · <code>measure-code-distance git-diff</code>, same excludes as the notebook · <code>public/layout-corrected.csv</code> from <code>scripts/layout_corrected/</code> · 2026-10-29</div>


---

<div class="eyebrow">BACKUP · PORT RUN-TIME SPEED · V1 ONLY · claude-opus-5 · high effort</div>

<MeasurePanels src="/v1-ladder-runs.csv" by="condition-v1" :measures="['ladder_ref_ratio']" :reference-line="1" :width="520" :height="150" />

<div class="source">V1 only; V2 did not measure speed · one dot = one port; 42 ports, 37 completed the ladder · ladder = a fixed sequence of grammars parsed in order, timed · value = port's ladder time ÷ handwritten reference's ladder time; 1.0 = same speed, below the line is faster · columns = which tests the agent saw · published article · 2026-09</div>
