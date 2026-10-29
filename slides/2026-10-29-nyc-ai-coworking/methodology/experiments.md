<div class="eyebrow">METHODOLOGY · THREE EXPERIMENTS</div>

# Three experiments, one grammar library, both directions

<div class="big-steps">
  <div><strong>V1 · pilot</strong><span>claude-opus-5, high effort. Which tests the agent sees: none, source, target, both. 42 ports. Measured size, speed, similarity, test pass rate. Found the <code>__pycache__</code> leak.</span></div>
  <div><strong>V2 · models × effort</strong><span>Fable, Opus, Sonnet, Haiku × low, medium, high, very high. Unit and source tests always included. 12 repeats per cell and direction. 384 ports; the max runs are still finishing and are not shown.</span></div>
  <div><strong>V2 · tests</strong><span>claude-opus-5-5, medium effort. Every combination of unit, source and target tests on or off: 8 conditions. 12 repeats per condition and direction. 192 ports.</span></div>
</div>

<div class="source">Each port: one agent, one sandbox, the reference mounted read-only at <code>/input</code>, no network · source = language-agnostic integration tests in the source language, target = the same tests in the target language · 2026-09 to 2026-10</div>
