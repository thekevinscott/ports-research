---
theme: default
colorSchema: light
title: Can an Agent Port a Codebase?
layout: cover
---

<div class="eyebrow">NYC AI Co-working · 2026-10-29</div>

# Asking Agents To<br>Port Codebases

<div class="cover-meta">Kevin Scott</div>

---

<div class="eyebrow">OVERVIEW</div>

# One library, two hand-written versions, 617 agent ports

<div class="toc">
  <div>
    <div class="toc-section"><i>01</i> Methodology</div>
    <ol>
      <li>The library: <code>gbnf</code>, hand-written in Python and TypeScript</li>
      <li>The prompt the agent gets</li>
      <li>The <code>__pycache__</code> leak</li>
      <li>Three experiments: pilot, models × effort, tests</li>
    </ol>
  </div>
  <div>
    <div class="toc-section"><i>02</i> Results</div>
    <ol>
      <li>Tokens, time, cost, files, lines of code</li>
      <li>Similarity to the handwritten reference</li>
      <li>Held-out tests: does the port behave like the reference?</li>
      <li>Do repeats of one setting agree with each other?</li>
      <li>How fast the ported library runs</li>
      <li>What effect do the tests the agent sees have?</li>
    </ol>
    <div class="toc-section last"><i>03</i> Takeaways</div>
    <ol>
      <li>Which model and effort, for the money</li>
      <li>The agent has a house style; your port is the outlier</li>
      <li>Tests bought tokens, not code</li>
    </ol>
  </div>
</div>

<div class="source">V1 pilot 42 ports · v2-models-effort 383 ports (4 models × 4 efforts × 2 directions × 12) · v2-tests-configuration 192 ports (8 conditions × 2 directions × 12)</div>

---
layout: section
---

# Methodology

---
src: ./methodology/gbnf.md
---

---
src: ./methodology/prompt.md
---

---
src: ./methodology/pycache.md
---

---
src: ./methodology/experiments.md
---

---
layout: section
---

# Results

---
src: ./results/overall-stats.md
---

---
src: ./results/similarity.md
---

---
src: ./results/tests-behavior.md
---

---
src: ./results/port-matrix.md
---

---
src: ./results/speed.md
---

---
src: ./results/tests-effect.md
---


---
layout: section
---

# Takeaways

---
src: ./results/for-the-money.md
---

---
src: ./results/takeaway-house-style.md
---

---
src: ./results/takeaway-tests.md
---

---


<div class="end-layout">
  <div>
    <h1>The End. Questions?</h1>
    <div class="end-link">Slides and data: <strong>github.com/thekevinscott/ports-research</strong><br><span class="end-sub">slides/2026-10-29-nyc-ai-coworking</span></div>
  </div>
  <QrCode url="https://github.com/thekevinscott/ports-research/tree/main/slides/2026-10-29-nyc-ai-coworking" :size="240" />
</div>

---
src: ./backup/followups.md
---

---

<div class="eyebrow">B · NOTEBOOK · STATISTICAL ANALYSIS</div>

# Line similarity to the handwritten reference (%)

<div class="nb-row">
  <img src="/nb-reference-diff-similarity-pct-python-to-typescript.png">
  <img src="/nb-reference-diff-similarity-pct-typescript-to-python.png">
</div>

<table class="nb-table">
<thead><tr><th>median</th><th>neither</th><th>unit tests</th><th>target integration tests</th><th>both</th></tr></thead>
<tr><td>Python → TypeScript</td><td>39.50</td><td>41.02</td><td>41.26</td><td>43.44</td></tr>
<tr><td>TypeScript → Python</td><td>30.24</td><td>32.99</td><td>33.81</td><td>35.74</td></tr>
</table>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · n=24 per condition and direction · source integration tests pooled within each condition</div>

---

<div class="eyebrow">B · NOTEBOOK · STATISTICAL ANALYSIS</div>

# Line similarity between ports (%)

<div class="nb-row wide">
  <img src="/nb-port-to-port-similarity-pct.png">
  <table class="nb-table">
  <thead><tr><th>median</th><th>Py → TS</th><th>TS → Py</th></tr></thead>
  <tr><td>neither</td><td>76.09</td><td>58.75</td></tr>
  <tr><td>unit tests</td><td>78.45</td><td>66.52</td></tr>
  <tr><td>target integration tests</td><td>76.41</td><td>69.51</td></tr>
  <tr><td>both</td><td>76.61</td><td>73.57</td></tr>
  </table>
</div>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · every unordered pair of ports within a condition and direction · 276 pairs each</div>

---

<div class="eyebrow">B · NOTEBOOK · EMBEDDINGS</div>

# Embedding distance to the reference (Chamfer)

<div class="nb-row">
  <img src="/nb-embeddings-python-to-typescript.png">
  <img src="/nb-embeddings-typescript-to-python.png">
</div>

<table class="nb-table">
<thead><tr><th>median</th><th>neither</th><th>unit tests</th><th>target integration tests</th><th>both</th><th>calibration: rename</th><th>calibration: 25% files deleted</th></tr></thead>
<tr><td>Py → TS</td><td>0.044</td><td>0.039</td><td>0.038</td><td>0.036</td><td>0.024</td><td>0.022</td></tr>
<tr><td>TS → Py</td><td>0.064</td><td>0.061</td><td>0.061</td><td>0.053</td><td>0.030</td><td>0.043</td></tr>
</table>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · n=24 per condition and direction · qwen3-embedding-0.6b-q8_0 · 0 is identical · calibration rungs: the same measure on mutated copies of the target-language reference, 2026-09-10</div>

---

<div class="eyebrow">B · NOTEBOOK · HELD-OUT BEHAVIOUR</div>

# Held-out behaviour agreement with the reference (%)

<div class="nb-row wide">
  <img src="/nb-behavior-agreement-pct.png">
  <table class="nb-table small">
  <thead><tr><th>cell</th><th>Py → TS median</th><th>driven / 12</th><th>TS → Py median</th><th>driven / 12</th></tr></thead>
  <tr><td>none</td><td>97.5</td><td>9</td><td>99.37</td><td>11</td></tr>
  <tr><td>unit</td><td>56.2</td><td>2</td><td>0</td><td>0</td></tr>
  <tr><td>source</td><td>9.64</td><td>5</td><td>0</td><td>0</td></tr>
  <tr><td>target</td><td>97.5</td><td>11</td><td>99.37</td><td>11</td></tr>
  <tr><td>unit + source</td><td>97.5</td><td>8</td><td>39.8</td><td>3</td></tr>
  <tr><td>unit + target</td><td>97.5</td><td>11</td><td>99.37</td><td>12</td></tr>
  <tr><td>source + target</td><td>97.18</td><td>7</td><td>99.37</td><td>12</td></tr>
  <tr><td>all</td><td>97.5</td><td>12</td><td>99.37</td><td>12</td></tr>
  </table>
</div>

<div class="nb-note">Driver status over 192 runs: 126 driven · 39 loaded but failing · 27 not loaded. Of the 126 driven, 119 sit at 97.5% / 99.37% = 779 / 799 and 794 / 799; the 20 and 5 pairs left are the target reference's own bugs (20 emoji inputs, 5 past-the-end inputs).</div>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · 799 held-out grammar–input pairs · three-way comparison 2026-10-28</div>

---

<div class="eyebrow">B · NOTEBOOK · HELD-OUT API</div>

# Held-out API agreement with the reference (%)

<div class="nb-row wide">
  <img src="/nb-api-agreement-pct.png">
  <table class="nb-table small">
  <thead><tr><th>cell</th><th>Py → TS median</th><th>TS → Py median</th></tr></thead>
  <tr><td>none</td><td>87.79</td><td>94.89</td></tr>
  <tr><td>unit</td><td>10.51</td><td>9.01</td></tr>
  <tr><td>source</td><td>0</td><td>0</td></tr>
  <tr><td>target</td><td>87.79</td><td>94.89</td></tr>
  <tr><td>unit + source</td><td>87.79</td><td>9.01</td></tr>
  <tr><td>unit + target</td><td>87.79</td><td>94.89</td></tr>
  <tr><td>source + target</td><td>86.69</td><td>94.89</td></tr>
  <tr><td>all</td><td>87.79</td><td>94.89</td></tr>
  </table>
</div>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · n=12 per cell · held-out API corpus never shown to the agent</div>

---

<div class="eyebrow">B · NOTEBOOK · AST RELATIVE TO THE REFERENCE</div>

# Share of the reference's functions the port has a counterpart for

<div class="nb-row wide">
  <img src="/nb-ast-matched-fraction.png">
  <table class="nb-table small">
  <thead><tr><th>cell</th><th>Py → TS median</th><th>TS → Py median</th></tr></thead>
  <tr><td>none</td><td>0.78</td><td>0.76</td></tr>
  <tr><td>unit</td><td>0.79</td><td>0.75</td></tr>
  <tr><td>source</td><td>0.77</td><td>0.73</td></tr>
  <tr><td>target</td><td>0.75</td><td>0.66</td></tr>
  <tr><td>unit + source</td><td>0.81</td><td>0.75</td></tr>
  <tr><td>unit + target</td><td>0.79</td><td>0.78</td></tr>
  <tr><td>source + target</td><td>0.75</td><td>0.75</td></tr>
  <tr><td>all</td><td>0.77</td><td>0.76</td></tr>
  </table>
</div>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · n=12 per cell · functions pair by normalised name and arity</div>

---

<div class="eyebrow">B · NOTEBOOK · TRANSCRIPTS</div>

# What the agent did · medians, flag on / off

<div class="nb-row wide">
  <img src="/nb-own-tests-written.png">
  <table class="nb-table">
  <thead><tr><th>measure</th><th>flag</th><th>on</th><th>off</th></tr></thead>
  <tr><td>test files the agent wrote itself</td><td>unit</td><td>22.5</td><td>1</td></tr>
  <tr><td>test suite runs</td><td>unit</td><td>9.5</td><td>4</td></tr>
  <tr><td>reads of a file already read</td><td>unit</td><td>24.5</td><td>7</td></tr>
  <tr><td>files read before the first write</td><td>unit</td><td>55</td><td>42.5</td></tr>
  <tr><td>reads of the source language's shipped tests</td><td>unit</td><td>8</td><td>0</td></tr>
  <tr><td>reads of the target language's shipped tests</td><td>target</td><td>3</td><td>0</td></tr>
  </table>
</div>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · n=96 on / 96 off per flag · parsed from the agent transcripts</div>

---

<div class="eyebrow">B · NOTEBOOK · V2 STATISTICS</div>

# Per-flag comparison · median on − off, pooled over the other flags

<table class="nb-table">
<thead><tr><th>measure</th><th>unit tests</th><th>p</th><th>source integration tests</th><th>p</th><th>target integration tests</th><th>p</th></tr></thead>
<tr><td>behaviour agreement (pct points)</td><td>0</td><td>1.0</td><td>0</td><td>1.0</td><td>+57.7</td><td>0.0001</td></tr>
<tr><td>API agreement (pct points)</td><td>0</td><td>1.0</td><td>0</td><td>1.0</td><td>+82.33</td><td>0.0001</td></tr>
<tr><td>AST matched fraction</td><td>+0.03</td><td>0.0001</td><td>−0.01</td><td>0.77</td><td>−0.01</td><td>0.78</td></tr>
<tr><td>call-trace edit distance</td><td>+0.12</td><td>0.0001</td><td>+0.03</td><td>0.44</td><td>−0.12</td><td>0.0001</td></tr>
<tr><td>total tokens</td><td>+1.71M</td><td>0.0001</td><td>+0.48M</td><td>0.48</td><td>+0.17M</td><td>0.82</td></tr>
<tr><td>LOC</td><td>+30.5</td><td>0.0012</td><td>+4.5</td><td>0.71</td><td>+26</td><td>0.0023</td></tr>
</table>

<div class="nb-note">Notebook's own caveat: "This section runs 135 comparisons with a p, none corrected for the others. If no flag changed any measure, about 7 of them would still give p &lt; 0.05. Every p here is exploratory."</div>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · n=96 on / 96 off per flag · p from 10,000 label shuffles, seed 0</div>

---

<div class="eyebrow">B · NOTEBOOK · JUDGE · CODE RUBRIC</div>

# Code judge · counts of 24 per condition and source language

<table class="nb-table small">
<thead><tr><th>item</th><th>value</th><th colspan="4">Python source · neither / unit / target / both</th><th colspan="4">JavaScript source · neither / unit / target / both</th></tr></thead>
<tr><td>fidelity</td><td>score 4</td><td>24</td><td>24</td><td>24</td><td>24</td><td>22</td><td>19</td><td>15</td><td>17</td></tr>
<tr><td>fidelity</td><td>score 3</td><td>0</td><td>0</td><td>0</td><td>0</td><td>2</td><td>5</td><td>9</td><td>7</td></tr>
<tr><td>api_parity</td><td>complete</td><td colspan="4">1 of 96 (rest minor-gaps)</td><td>20</td><td>17</td><td>22</td><td>23</td></tr>
<tr><td>semantic divergences</td><td>ordinary-inputs</td><td colspan="4">1 of 96 (rest edge-inputs-only)</td><td>2</td><td>5</td><td>9</td><td>8</td></tr>
<tr><td>idiom</td><td>idiomatic</td><td>19</td><td>19</td><td>24</td><td>23</td><td colspan="4">mixed: 24 / 24 / 22 / 24</td></tr>
<tr><td>dropped or added</td><td></td><td colspan="4">both: 96 of 96</td><td colspan="4">added: 17 / 17 / 18 / 23</td></tr>
</table>

<div class="nb-note">Human baseline, the two handwritten implementations judged against each other blind: fidelity 3 in both directions.</div>

<div class="source">Notebook · v2-tests-configuration · 2026-10-29 · one blind prompt per port to claude-opus-5-5 at effort max · reference as A, port as B · tests and build files left out</div>
