---
theme: default
colorSchema: light
title: Can an Agent Port a Codebase?
layout: cover
---

<div class="eyebrow">PORTS · 2026-10-29</div>

# Can an Agent<br>Port a Codebase?

<div class="cover-meta">Kevin Scott</div>

---

<div class="eyebrow">01 · THE QUESTION</div>

# For those of us without a datacenter at our disposal, how realistic are these code translation efforts?

<div class="subline">Bun: Zig → Rust &nbsp;·&nbsp; Mistral: Fortran → C++</div>

<div class="quote-bottom">“Can an agent take a smaller repo running on a personal laptop and turn out a reasonably faithful port?”</div>

---

<div class="eyebrow">02 · V1 EXPERIMENT</div>

# The experiment

<div class="setup-grid">
  <div><strong>gbnf</strong><span>Handwritten Python + TypeScript</span></div>
  <div><strong>Sandbox</strong><span>Target implementation hidden</span></div>
  <div><strong>claude-opus-5</strong><span>High effort</span></div>
  <div><strong>40 ports</strong><span>2 directions × 4 test conditions × 5</span></div>
</div>

<div class="source">Published article · 2026-09-15</div>

---

<div class="eyebrow">03 · V1 EXPERIMENT</div>

# The Agent, Uh, Finds a Way

<div class="leak-word">__pycache__</div>

<div class="leak-lines">
  <p>“The agents discovered the <code>__pycache__</code> folders and were able to reconstruct the missing tests.”</p>
  <p>“Eight saw the bytecode, four used it.”</p>
</div>

<div class="source">Python → TypeScript only · Published article</div>

---

<div class="eyebrow">04 · V1 RESULTS</div>

# The ports were smaller and faster

<div class="four-charts">
  <div><img src="/size-python-to-typescript.svg"><span>Python → TypeScript · size</span></div>
  <div><img src="/size-typescript-to-python.svg"><span>TypeScript → Python · size</span></div>
  <div><img src="/ladder-ref-ratio-python-to-typescript.svg"><span>Python → TypeScript · speed</span></div>
  <div><img src="/ladder-ref-ratio-typescript-to-python.svg"><span>TypeScript → Python · speed</span></div>
</div>

<div class="source">Published article · 40 ports · speed on completed rungs · size outliers not shown: 146 files; 2,075 LOC</div>

---

<div class="eyebrow">05 · V1 RESULTS</div>

# My handwritten implementation was the outlier

<div class="outlier-grid">
  <div class="heatmap"><img src="/port-to-port-matrix-python-to-typescript.svg"><span>Python → TypeScript · final column: handwritten reference</span></div>
  <div class="embedding">
    <div class="table-title">Embedding distance ↓</div>
    <table>
      <thead><tr><th>Direction</th><th>Port ↔ port</th><th>Port ↔ reference</th></tr></thead>
      <tbody>
        <tr><td>Py → TS</td><td>0.0171</td><td>0.0416</td></tr>
        <tr><td>TS → Py</td><td>0.0447</td><td>0.0656</td></tr>
      </tbody>
    </table>
    <p>“Most ports cluster closer to each other than they do to my implementation.”</p>
  </div>
</div>

<div class="source">Published article · pairwise line similarity and embedding distance</div>

---

<div class="eyebrow">06 · FAITHFULNESS</div>

# What constitutes a faithful port?

<div class="examples">
  <div><strong>Type exports</strong><span>“Python libraries often don't do this.”</span></div>
  <div><strong>Operator overloading</strong><span>“JavaScript does not support operator overloading.”</span></div>
  <div><strong>Sync / async</strong><span>“Should the Python port offer both sync and async versions?”</span></div>
</div>

<div class="source">Published article</div>

---

<div class="eyebrow">07 · V2 DESIGN</div>

# Two studies

<div class="studies">
  <div>
    <h2>Tests configuration</h2>
    <p>claude-opus-5-5 · medium</p>
    <p>unit / source / target test flags</p>
    <strong>2 directions × 8 × 12 = 192</strong>
  </div>
  <div>
    <h2>Models × effort</h2>
    <p>fable-5-1 · opus-5-5 · sonnet-5-5 · haiku-5-5</p>
    <p>low · medium · high</p>
    <strong>12 per cell, per direction · design</strong>
  </div>
</div>

<div class="source">V2 experiment designs · 2026-10-28</div>

---

<div class="eyebrow">08 · V2 TESTS CONFIGURATION</div>

# Tests change the port in three ways

<div class="findings">
  <div><strong>Driven ports</strong><p>Target tests: <b>88 / 96</b><br>None: <b>20 / 24</b><br>Unit or source only: <b>18 / 72</b></p></div>
  <div><strong>Median behaviour · driven</strong><p>Py → JS: <b>97.5%</b><br>JS → Py: <b>99.4%</b><br>JS → Py, unit + source: <b>86.1%</b> (n=3)</p></div>
  <div><strong>Unit tests · on / off</strong><p>Median tokens: <b>2.9M / 1.2M</b><br>Paired share: <b>0.78 / 0.75</b></p></div>
</div>

<img class="tests-chart" src="/tests-total-tokens.png">

<div class="source">Test-inclusion report · 2026-10-12 · n = 192 successful runs</div>

---

<div class="eyebrow">09 · V2 MODELS × EFFORT</div>

# Models × effort · runs to date

<ModelsEffortChart />

<div class="source">v2-models-effort · successful, non-excluded runs · low / medium / high only · measured 2026-10-28</div>

---

<div class="eyebrow">10 · OPEN QUESTION</div>

# What makes for a faithful port?

<div class="closing-quote">“So I think we need a more holistic measure of what it means to be ‘faithful’.”</div>

<div class="closing-secondary">“How faithful are the ports? That, I think, is still to be determined.”</div>

<div class="source">V2 draft · Published article</div>
