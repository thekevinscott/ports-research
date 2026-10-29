<div class="eyebrow">TAKEAWAYS</div>

# Three things the 617 ports say

<div class="takeaway-list">
<div class="takeaway-item"><i>1</i><div><b>For the money: Opus.</b><span>$5 – 9 per port that runs, at medium or high effort. Haiku never produced a port that ran. Fable ran more often Python → TypeScript and cost 1.2 – 11× more per working port.</span></div></div>
<div class="takeaway-item"><i>2</i><div><b>The agent has a house style. Handwritten implementations are the outlier.</b><span>Two ports of the same setting share 61 – 66 % of their lines. A port and the handwritten version share 33 – 38 %.</span></div></div>
<div class="takeaway-item"><i>3</i><div><b>Target-language integration tests are cheap insurance. Source-language tests on their own are not enough, and can hurt.</b><span>Target tests did not beat no tests: 88 – 95 % held-out API agreement either way. But they were the only tests that told the agent the interface. Source-language tests alone: 7 – 8 of 12 ports would not load. Target tests undid that, for fewer tokens than no tests.</span></div></div>
</div>

<div class="source">v2-models-effort (383 runs) and v2-tests-configuration (192 runs) · one drill-down slide per takeaway follows<span class="date">2026-10-29</span></div>
