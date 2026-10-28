---
theme: default
colorSchema: light
title: Can an Agent Port a Codebase?
layout: cover
---

<div class="eyebrow">PORTS · 2026-10-29</div>

# Can an Agent<br>Port a Codebase?

<div class="cover-question">Can an agent turn out a reasonably faithful port?</div>

<div class="cover-meta">Kevin Scott</div>

---

<div class="eyebrow">SETUP</div>

# One library, two languages

<div class="setup-flow">
  <div><strong>gbnf</strong><span>Handwritten Python + TypeScript</span></div>
  <div><strong>Agent</strong><span>Sandboxed port · one language to the other</span></div>
  <div><strong>Compare</strong><span>Agent port ↔ handwritten implementation</span></div>
</div>

<div class="source">Published article · 2026-09-15</div>

---
layout: section
---

<div class="section-index">A / V1</div>

# The Agent, Uh,<br>Finds a Way

<div class="section-subtitle">__pycache__</div>

---

<div class="eyebrow">A · WHAT WE ASKED</div>

# Port Python → TypeScript

<div class="big-steps">
  <div><strong>Python source</strong><span>Visible to the agent</span></div>
  <div><strong>TypeScript target</strong><span>Hidden from the agent</span></div>
  <div><strong>Tests</strong><span>Withheld in selected conditions</span></div>
</div>

<div class="source">Published article · V1 · claude-opus-5, high effort</div>

---

<div class="eyebrow">A · WHAT IT PRODUCED</div>

# It found the missing tests

<div class="leak-word">__pycache__</div>

<div class="leak-lines">“The agents discovered the <code>__pycache__</code> folders and were able to reconstruct the missing tests.”</div>

<a class="memory-link" href="https://github.com/thekevinscott/ports-research/blob/v1.1/packages/gbnf-experiment/data/20260909T005215Z_9a3e20fe/transcript/-workspace/memory/gbnf-reference-tests-in-pycache.md">Agent transcript memory: gbnf-reference-tests-in-pycache.md ↗</a>

<div class="source">Published article · agent transcript memory file</div>

---

<div class="eyebrow">A · WHAT EVALUATION SHOWED</div>

# Eight saw the bytecode. Four used it.

<div class="result-split">
  <div><strong>8</strong><span>saw the bytecode</span></div>
  <div><strong>4</strong><span>used it</span></div>
  <div><strong>½</strong><span>test-setup results discarded</span></div>
</div>

<div class="result-note">Cached test bytecode reached the agent when tests were meant to be withheld.</div>

<div class="source">Python → TypeScript · Published article</div>

---

<div class="eyebrow">A · TAKEAWAY</div>

# Lesson

<div class="lesson-todo">TODO: Kevin</div>

---
layout: section
---

<div class="section-index">B / V2</div>

# What do tests change?

<div class="section-subtitle">Tests configuration</div>

---

<div class="eyebrow">B · WHAT WE ASKED</div>

# Three test flags

<div class="flag-grid">
  <div><strong>unit</strong><span>Source-language unit tests</span></div>
  <div><strong>source</strong><span>Source-language integration tests</span></div>
  <div><strong>target</strong><span>Target-language integration tests</span></div>
</div>

<div class="study-line">claude-opus-5-5 · medium · 2 directions × 8 combinations × 12 = 192 ports</div>

<div class="source">Test-inclusion report · 2026-10-12 · n=192</div>

---

<div class="eyebrow">B · WHAT IT PRODUCED</div>

# Unit tests: far more work, structure nudged

<div class="finding-line"><strong>2.9M / 1.2M</strong><span>median tokens · unit on / off</span></div>
<div class="finding-line"><strong>22.5 / 1</strong><span>own test files · unit tests on / off</span></div>
<div class="finding-line"><strong>0.78 / 0.75</strong><span>reference functions paired · unit on / off</span></div>

<img class="finding-chart" src="/tests-total-tokens.png">

<div class="source">Test-inclusion report · 2026-10-12 · n=192 · chart: total tokens</div>

---

<div class="eyebrow">B · WHAT EVALUATION SHOWED</div>

# Interface, then behaviour

<div class="two-findings">
  <div><strong>Target tests: 88 / 96 driven</strong><span>No tests: 20 / 24 · unit or source only: 18 / 72</span><img src="/tests-behavior-agreement.png"></div>
  <div><strong>Driven ports: 97.5% / 99.4%</strong><span>Median behaviour · Py → JS / JS → Py · exception: 86.1% (n=3)</span><img src="/tests-behavior-driven.png"></div>
</div>

<div class="source">Test-inclusion report · 2026-10-12 · n=192 · held-out behaviour</div>

---

<div class="eyebrow">B · TAKEAWAY</div>

# Lesson

<div class="lesson-todo">TODO: Kevin</div>

---
layout: section
---

<div class="section-index">C / V2</div>

# Models × effort

<div class="section-subtitle">Low · medium · high</div>

---

<div class="eyebrow">C · WHAT WE ASKED</div>

# Four models × three efforts

<div class="model-grid">
  <div>fable-5-1</div><div>opus-5-5</div><div>sonnet-5-5</div><div>haiku-5-5</div>
</div>

<div class="study-line">Python ↔ JavaScript · low / medium / high · 12 ports per model × effort × direction</div>

<div class="source">v2-models-effort design · 2026-10-28 · xhigh / max omitted</div>

---

<div class="eyebrow">C · WHAT IT PRODUCED</div>

# Port size · files and LOC

<ModelsEffortChart initial-measure="file_count" />

<div class="source">v2-models-effort · n=12 per cell and direction · 2026-10-28</div>

---

<div class="eyebrow">C · WHAT EVALUATION SHOWED</div>

# Wall time and tokens

<ModelsEffortChart show-setup-footnote />

<div class="source">v2-models-effort · n=12 per cell and direction · 2026-10-28</div>

---

<div class="eyebrow">C · TAKEAWAY</div>

# Lesson

<div class="lesson-todo">TODO: Kevin</div>

---

<div class="eyebrow">BACKUP · V1 RESULTS</div>

# Smaller, faster; my code was the outlier

<div class="backup-grid">
  <div><img src="/size-python-to-typescript.svg"><span>Size · Python → TypeScript</span></div>
  <div><img src="/ladder-ref-ratio-python-to-typescript.svg"><span>Speed · Python → TypeScript</span></div>
  <div><img src="/port-to-port-matrix-python-to-typescript.svg"><span>Similarity · Python → TypeScript</span></div>
</div>

<div class="backup-numbers">Embedding distance · port ↔ port <b>0.0171</b> · port ↔ reference <b>0.0416</b></div>

<div class="source">Published article · V1 · Python → TypeScript</div>

---

<div class="eyebrow">CLOSE</div>

# What makes for a faithful port?

<div class="closing-quote">“So I think we need a more holistic measure of what it means to be ‘faithful’.”</div>

<div class="source">V2 draft</div>

---
layout: section
---

# Questions
