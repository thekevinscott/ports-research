<div class="eyebrow">METHODOLOGY · THREE EXPERIMENTS</div>

# Three experiments, one library, both directions

<div class="big-steps">
  <div><strong>V1 · pilot</strong><span>claude-opus-5, high effort. Which tests the agent sees: none, source, target, both. Measured size, speed, similarity, test pass rate. Found the <code>__pycache__</code> leak.</span><em>4 conditions × 2 directions · 5 runs per cell (7 in one) · <b>42 ports</b><br>$286 · 329 M tokens · 10 h agent time</em></div>
  <div><strong>V2 · models × effort</strong><span>Fable, Opus, Sonnet, Haiku × low, medium, high, very high. Unit and source tests always included. The max runs are still finishing and are not shown.</span><em>16 cells × 2 directions · 12 runs per cell (11 in one) · <b>383 ports</b><br>$1,561 · 2,135 M tokens · 98 h agent time<br>+ 30 max runs in flight: $414 · 872 M · 32 h</em></div>
  <div><strong>V2 · tests</strong><span>claude-opus-5-5, medium effort. Every combination of unit, source and target tests on or off.</span><em>8 conditions × 2 directions · 12 runs per cell · <b>192 ports</b><br>$387 · 411 M tokens · 23 h agent time</em></div>
</div>

<div class="source">Each port: one agent, one sandbox, the reference mounted read-only at <code>/input</code>, no network · source = language-agnostic integration tests in the source language, target = the same tests in the target language · $ = Claude Code's <code>total_cost_usd</code> at list price, summed · tokens include cache reads and writes · agent time = wall-clock inside the sandbox, summed, not calendar time · 2026-09 to 2026-10</div>
