<div class="eyebrow">TAKEAWAY 3 · SOURCE-LANGUAGE INTEGRATION TESTS BROKE THE PORT. TARGET-LANGUAGE TESTS FIXED IT.</div>

# The wrong tests bought broken ports. The right ones bought tokens.

<RunStrips compact src="/tests-configuration-runs.csv" by="condition" initial-measure="api_agreement_pct" :measures="['api_agreement_pct', 'behavior_agreement_pct', 'total_tokens']" />

<div class="study-line">No tests: 95 % held-out API agreement. Unit or source-language tests alone: 8 of 12 ports would not load. Target-language tests brought it back to 95 %. Unit tests on top: 2 – 3× the tokens.</div>

<div class="source">v2-tests-configuration · Opus medium · n = 12 successful runs per cell · "would not load" = in the held-out driver · <code>public/tests-configuration-runs.csv</code> · 2026-10-29</div>
