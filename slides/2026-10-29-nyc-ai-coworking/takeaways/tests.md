<div class="eyebrow">TAKEAWAY 3 · SOURCE-LANGUAGE INTEGRATION TESTS BROKE THE PORT. TARGET-LANGUAGE TESTS FIXED IT.</div>

# Held-out API agreement by the test suites the agent was given

<table class="nb-table money pairs">
<thead><tr><th>tests the agent was given</th><th>Python → TypeScript</th><th>TypeScript → Python</th></tr></thead>
<tbody>
<tr><td>no tests</td><td>88 %</td><td>95 %</td></tr>
<tr><td>source integration</td><td class="hot">0 %</td><td class="hot">0 %</td></tr>
<tr><td>target integration</td><td>88 %</td><td>95 %</td></tr>
<tr><td>source + target integration</td><td>87 %</td><td>95 %</td></tr>
</tbody>
</table>

<div class="nb-note">Median held-out API agreement over 12 runs per cell, Opus medium: the share of the held-out driver's calls the port answers like the handwritten implementation. Orange = most ports in the cell would not load. Target tests do not beat no tests; they undo what source tests broke.</div>

<div class="source">v2-tests-configuration · n = 12 per cell and direction · drivers in <code>analysis/measure-behavior/drivers/</code> · <code>public/tests-configuration-runs.csv</code> · 2026-10-29</div>
