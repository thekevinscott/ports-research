<div class="eyebrow">APPENDIX · SIMILARITY ONCE THE PACKAGE IS MOVED TO WHERE THE REFERENCE KEEPS IT</div>

# Move the folder, fix the case, re-measure

<table class="nb-table small" style="width:auto">
<thead><tr><th>direction</th><th>model</th><th>misplaced ports</th><th>as scored</th><th>folder moved</th><th>also renamed</th><th>final</th></tr></thead>
<tr><td>TypeScript → Python</td><td>Fable</td><td>6</td><td>6.3</td><td>33.7</td><td>0</td><td class="hot">33.7</td></tr><tr><td>TypeScript → Python</td><td>Opus</td><td>1</td><td>0.3</td><td>32.1</td><td>0</td><td class="hot">32.1</td></tr><tr><td>TypeScript → Python</td><td>Haiku</td><td>41</td><td>1.3</td><td>34.5</td><td>0</td><td class="hot">34.5</td></tr><tr><td>Python → TypeScript</td><td>Opus</td><td>23</td><td>8.0</td><td>8.3</td><td>23</td><td class="hot">37.5</td></tr><tr><td>Python → TypeScript</td><td>Sonnet</td><td>33</td><td>1.2</td><td>1.3</td><td>33</td><td class="hot">27.0</td></tr><tr><td>Python → TypeScript</td><td>Haiku</td><td>30</td><td>8.7</td><td>36.3</td><td>6</td><td class="hot">37.4</td></tr></table>

<div class="nb-note">The 134 ports whose package is not where the reference keeps it, copied to scratch and re-scored with the same git-diff measure after two mechanical fixes, nothing inside any file changed. First the package directory is moved (<code>python/gbnf → gbnf</code>, <code>gbnf → src</code>, and so on). That alone lifts every TypeScript → Python port to 32–35 %. 62 Python → TypeScript ports (all Sonnet, all Opus, 6 Haiku) still match nothing because they name folders <code>rules_builder/</code> where the reference has <code>rules-builder/</code>; lower-casing and dashing those names lifts them to 27–38 %. Medians in the "final" column use the renamed score where a rename was applied. The lowest of the 134 after both fixes is 20.0 %.</div>

<div class="source">v2-models-effort · <code>measure-code-distance git-diff</code>, same excludes as the notebook · <code>public/layout-corrected.csv</code> from <code>scripts/layout_corrected/</code><span class="date">2026-10-29</span></div>
