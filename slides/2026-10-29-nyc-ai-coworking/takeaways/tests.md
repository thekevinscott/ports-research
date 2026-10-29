<div class="eyebrow">TAKEAWAY 3 · TARGET-LANGUAGE INTEGRATION TESTS ARE CHEAP INSURANCE. SOURCE-LANGUAGE TESTS ON THEIR OWN ARE NOT ENOUGH, AND CAN HURT.</div>

# Held-out API agreement by the test suites the agent was given

<table class="nb-table money pairs wide">
<thead><tr><th>tests the agent was given</th><th colspan="2">Python → TypeScript</th><th colspan="2">TypeScript → Python</th></tr>
<tr><th></th><th>API agreement</th><th>loaded</th><th>API agreement</th><th>loaded</th></tr></thead>
<tbody>
<tr><td>no tests</td><td>88 %</td><td class="ran">12 of 12</td><td>95 %</td><td class="ran">12 of 12</td></tr>
<tr><td>source integration</td><td class="hot">0 %</td><td class="ran">5 of 12</td><td class="hot">0 %</td><td class="ran">4 of 12</td></tr>
<tr><td>target integration</td><td>88 %</td><td class="ran">11 of 12</td><td>95 %</td><td class="ran">11 of 12</td></tr>
<tr><td>source + target integration</td><td>87 %</td><td class="ran">7 of 12</td><td>95 %</td><td class="ran">12 of 12</td></tr>
</tbody>
</table>

<div class="nb-note">Median held-out API agreement over 12 runs per cell, Opus medium: the share of the held-out driver's calls the port answers like the handwritten implementation. A port that did not load scores 0 %. Orange = most ports in the cell would not load. Target tests do not beat no tests. They are the only condition that told the agent the interface the driver expects; given source tests alone, the agent chose its own package layout and the driver could not import it. Target integration tests also cost fewer tokens than no tests.</div>

<div class="source">v2-tests-configuration · n = 12 per cell and direction · drivers in <code>analysis/measure-behavior/drivers/</code> · <code>public/tests-configuration-runs.csv</code> · 2026-10-29</div>
