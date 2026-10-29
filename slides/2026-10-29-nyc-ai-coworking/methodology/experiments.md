<div class="eyebrow">METHODOLOGY · THREE EXPERIMENTS</div>

# Which model, effort and tests give a port that works, and at what cost?

<div class="explain">Three experiments, one library, both directions. Each port: one agent, one sandbox, the reference read-only, no network.</div>

<div class="big-steps">
  <div><strong>V1 · pilot</strong><span>Opus 5, high effort. Vary which tests the agent sees. Found the <code>__pycache__</code> leak.</span><em>4 conditions × 2 directions · <b>42 ports</b> · $286</em></div>
  <div><strong>V2 · models × effort</strong><span>Fable, Opus, Sonnet, Haiku × low, medium, high, very high. Unit and source tests always on.</span><em>16 cells × 2 directions × 12 runs · <b>383 ports</b> · $1,528</em></div>
  <div><strong>V2 · tests</strong><span>Opus 5.5, medium effort. Every combination of unit, source and target tests on or off.</span><em>8 conditions × 2 directions × 12 runs · <b>192 ports</b> · $355</em></div>
</div>

<div class="source">source = language-agnostic integration tests in the source language, target = the same tests in the target language · $ = every API call in the transcripts at Claude API list rates (V1: Claude Code's own figure) · 30 max-effort runs excluded · 2026-09 to 2026-10</div>
