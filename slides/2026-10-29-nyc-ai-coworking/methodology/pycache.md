<div class="eyebrow">METHODOLOGY · THE __pycache__ DISCOVERY</div>

# "Cheating": hard to prevent, harder to define

<div class="leak-lines pycache-quote top">“Let me extract the original test expectations from the leftover <code>.pyc</code> test files — they're a real spec for behavior.”</div>

<div class="big-steps pycache-steps two">
  <div><strong>What happened</strong><span>V1 withheld the tests. A host-side pytest run had left them compiled in <code>__pycache__</code>, mounted read-only beside the source. 8 runs had them. 4 decompiled them. 3 shipped the recovered tests.</span></div>
  <div><strong>Was that cheating?</strong><span>The agent broke no rule. It read a file in <code>/input</code>, where we said the reference lives. The boundary was ours to draw, and we drew it wrong.</span></div>
</div>

<div class="pycache-routes">
  <div><strong>__pycache__</strong><span>bytecode holds full source</span></div>
  <div><strong>.pytest_cache</strong><span>lists the failing test ids</span></div>
  <div><strong>npm · PyPI</strong><span>gbnf is published on both</span></div>
  <div><strong>sourcemaps</strong><span>json2gbnf bundles gbnf's source</span></div>
  <div><strong>training data</strong><span>the repo is public</span></div>
</div>

<div class="source">Agent transcript, run 20260909T130706Z_31ac2789, line 52 · Published article 2026-09-15</div>
