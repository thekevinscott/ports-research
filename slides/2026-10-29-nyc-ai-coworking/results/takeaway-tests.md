<div class="eyebrow">TAKEAWAY 3 · TESTS BOUGHT TOKENS, NOT CODE</div>

# Handing the agent tests changed how much it spent, not how much it wrote

<div class="finding-line"><strong>910 – 1,064</strong><span>median lines of code per port across all eight test conditions, both directions. Files: 32 to 38. The port is the same size whether the agent saw no tests, unit tests, integration tests, or all three.</span></div>
<div class="finding-line"><strong>2 – 3×</strong><span>tokens when unit tests were in the mix: 2.5 to 3.3 M per port versus 0.8 to 1.6 M without them.</span></div>
<div class="finding-line"><strong>8 of 12</strong><span>TypeScript → Python ports the held-out driver could not load when the agent saw only unit tests, and 8 of 12 with only source-language integration tests. With no tests: 1 of 12. With all three: 0 of 12, and every port scored 90 % or better.</span></div>

<div class="study-line">Partial test context cost more than none, in tokens and in ports that would not load. The full set cost the most and every port loaded.</div>

<div class="source">v2-tests-configuration · Opus medium · n=12 per condition and direction · <code>public/tests-configuration-runs.csv</code> · 2026-10-29</div>
