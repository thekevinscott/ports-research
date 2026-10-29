<div class="eyebrow">TAKEAWAY 3 · TESTS CHANGED WHAT THE PORT DID, NOT HOW BIG IT WAS</div>

# The wrong tests bought broken ports. The right ones bought tokens.

<div class="finding-line"><strong>910 – 1,064</strong><span>median lines per port across all eight test conditions, both directions; files 32 – 38. Size moved under 15 %.</span></div>
<div class="finding-line"><strong>0 – 9 % vs 95 %</strong><span>TypeScript → Python held-out API agreement with only source-language tests or only unit tests, versus 95 % with no tests and 95 % whenever target-language tests were in the set. Behaviour: 0 – 40 % vs 99 %. 8 of 12 ports in each of those two conditions would not load; with no tests, 1 of 12; with target-language tests, 0 – 1 of 12.</span></div>
<div class="finding-line"><strong>2 – 3×</strong><span>tokens whenever unit tests were in the set (2.5 – 3.3 M versus 0.8 – 1.6 M). Target-language integration tests alone cost 0.9× of no tests, with the same 95 % agreement.</span></div>

<div class="study-line">No tests worked. Source-language or unit tests alone broke the port; target-language tests fixed it; unit tests on top doubled the bill. Python → TypeScript: same shape, smaller gaps.</div>

<div class="source">v2-tests-configuration · Opus medium · n = 12 successful runs per cell (267 attempts, 75 non-zero exits dropped) · medians · "would not load" = in the held-out driver · <code>public/tests-configuration-runs.csv</code> · 2026-10-29</div>
