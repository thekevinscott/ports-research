<div class="eyebrow">APPENDIX · WHAT THE STUDY TOOK</div>

<div class="nb-row wide">
<table class="nb-table small">
<thead><tr><th></th><th>runs</th><th>spend</th><th>tokens</th><th>agent time</th></tr></thead>
<tr class=""><td>models × effort (incl. 30 max)</td><td>413</td><td>$1,912</td><td>3,007 M</td><td>130 h</td></tr><tr class=""><td>&nbsp;&nbsp;Fable</td><td>105</td><td>$1,081</td><td>426 M</td><td>39 h</td></tr><tr class=""><td>&nbsp;&nbsp;Opus</td><td>103</td><td>$536</td><td>777 M</td><td>37 h</td></tr><tr class=""><td>&nbsp;&nbsp;Sonnet</td><td>99</td><td>$173</td><td>527 M</td><td>20 h</td></tr><tr class=""><td>&nbsp;&nbsp;Haiku</td><td>106</td><td>$122</td><td>1,277 M</td><td>34 h</td></tr>
<tr class=""><td>tests experiment (Opus medium)</td><td>192</td><td>$355</td><td>411 M</td><td>23 h</td></tr>
<tr class="hot"><td>both</td><td>605</td><td>$2,267</td><td>3,418 M</td><td>153 h</td></tr>
<tr><td colspan="5" class="dim">models × effort spend by what the held-out driver could do with the port</td></tr>
<tr class=""><td>&nbsp;&nbsp;driver ran the port</td><td>102</td><td>$804</td><td>782 M</td><td>46 h</td></tr><tr class=""><td>&nbsp;&nbsp;loaded, failing</td><td>123</td><td>$676</td><td>815 M</td><td>39 h</td></tr><tr class=""><td>&nbsp;&nbsp;not loaded</td><td>188</td><td>$432</td><td>1,410 M</td><td>46 h</td></tr>
</table>
<table class="nb-table small" style="width:auto">
<thead><tr><th>driven ports</th><th>Python → TypeScript</th><th>TypeScript → Python</th></tr></thead>
<tr><td>Fable</td><td>32 / 52</td><td>6 / 53</td></tr><tr><td>Opus</td><td>25 / 54</td><td>24 / 49</td></tr><tr><td>Sonnet</td><td>5 / 49</td><td>10 / 50</td></tr><tr><td>Haiku</td><td>0 / 56</td><td>0 / 50</td></tr>
</table>
</div>

<div class="nb-note">Spend is every API call in the transcripts priced at Claude API list rates, summed; tokens are input, output and cache reads and writes from the transcripts. Agent time is wall-clock inside the container, summed, not calendar time: batches ran in parallel over about two weeks. Haiku used the most tokens of any model and the least money.</div>

<div class="source">v2-models-effort (413 runs) and v2-tests-configuration (192 runs) · <code>public/models-effort-runs.csv</code>, <code>public/tests-configuration-runs.csv</code>, <code>public/models-effort-status.csv</code> · 2026-10-29</div>
