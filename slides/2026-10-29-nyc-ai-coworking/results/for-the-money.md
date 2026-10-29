<div class="eyebrow">RESULTS · WHICH MODEL AND EFFORT, FOR THE MONEY?</div>

<table class="nb-table small">
<thead><tr><th>model</th><th>effort</th><th colspan="3">Python → TypeScript</th><th colspan="3">TypeScript → Python</th></tr>
<tr><th></th><th></th><th>median cost</th><th>driven</th><th>$ per driven port</th><th>median cost</th><th>driven</th><th>$ per driven port</th></tr></thead>
<tr><td>Fable</td><td>low</td><td>$6.67</td><td>4 / 12</td><td class="">$20</td><td>$6.43</td><td>0 / 12</td><td class="">–</td></tr>
<tr><td>Fable</td><td>medium</td><td>$7.92</td><td>5 / 12</td><td class="">$20</td><td>$7.29</td><td>1 / 12</td><td class="">$89</td></tr>
<tr><td>Fable</td><td>high</td><td>$10.01</td><td>11 / 12</td><td class="hot">$11</td><td>$8.92</td><td>2 / 12</td><td class="">$52</td></tr>
<tr><td>Fable</td><td>very high</td><td>$14.36</td><td>8 / 12</td><td class="">$23</td><td>$13.10</td><td>2 / 12</td><td class="">$83</td></tr>
<tr><td>Opus</td><td>low</td><td>$2.34</td><td>7 / 12</td><td class="hot">$3</td><td>$1.05</td><td>0 / 12</td><td class="">–</td></tr>
<tr><td>Opus</td><td>medium</td><td>$3.06</td><td>4 / 12</td><td class="hot">$9</td><td>$2.64</td><td>4 / 12</td><td class="hot">$9</td></tr>
<tr><td>Opus</td><td>high</td><td>$3.74</td><td>5 / 12</td><td class="hot">$9</td><td>$3.69</td><td>9 / 12</td><td class="hot">$5</td></tr>
<tr><td>Opus</td><td>very high</td><td>$8.63</td><td>6 / 12</td><td class="">$18</td><td>$8.15</td><td>11 / 12</td><td class="hot">$9</td></tr>
<tr><td>Sonnet</td><td>low</td><td>$0.48</td><td>0 / 12</td><td class="">–</td><td>$0.35</td><td>0 / 12</td><td class="">–</td></tr>
<tr><td>Sonnet</td><td>medium</td><td>$0.59</td><td>1 / 12</td><td class="hot">$7</td><td>$0.41</td><td>0 / 12</td><td class="">–</td></tr>
<tr><td>Sonnet</td><td>high</td><td>$1.10</td><td>0 / 12</td><td class="">–</td><td>$0.92</td><td>3 / 12</td><td class="hot">$4</td></tr>
<tr><td>Sonnet</td><td>very high</td><td>$3.65</td><td>4 / 12</td><td class="hot">$11</td><td>$3.71</td><td>5 / 12</td><td class="hot">$9</td></tr>
<tr><td>Haiku</td><td>low</td><td>$0.42</td><td>0 / 12</td><td class="">–</td><td>$0.48</td><td>0 / 12</td><td class="">–</td></tr>
<tr><td>Haiku</td><td>medium</td><td>$0.60</td><td>0 / 12</td><td class="">–</td><td>$0.54</td><td>0 / 12</td><td class="">–</td></tr>
<tr><td>Haiku</td><td>high</td><td>$0.89</td><td>0 / 12</td><td class="">–</td><td>$0.82</td><td>0 / 12</td><td class="">–</td></tr>
<tr><td>Haiku</td><td>very high</td><td>$1.49</td><td>0 / 11</td><td class="">–</td><td>$1.64</td><td>0 / 12</td><td class="">–</td></tr>
</table>

<div class="nb-note">$ per driven port = the cell's total spend ÷ ports the driver could run; it prices the attempts that fail too. Both directions pooled, cheapest first: Opus low $5 · Opus high $7 · Sonnet high $8 · Opus medium $9 · Sonnet very high $10. Haiku never produced a driven port at any effort.</div>

<div class="source">v2-models-effort · cost = Claude Code's <code>total_cost_usd</code> per run, list price · result.json usage is known to drop some calls, so cost may undercount · n = 12 per cell and direction · 2026-10-29</div>
