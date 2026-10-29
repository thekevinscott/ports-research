<div class="eyebrow">RESULTS · SIMILARITY BETWEEN PORTS · DO REPEATS OF ONE SETTING AGREE WITH EACH OTHER?</div>

<div class="explain">Each cell = median <b>diff lines</b> between two ports of the same setting (lines added + deleted in <code>git diff</code> after auto-formatting, over all 66 pairs among the cell's 12 ports). 0 = identical. Darker = the ports agree more. For scale, the same ports sit a median 1,700 – 3,000 diff lines from the handwritten version in the target language.</div>

<div class="tabs-row"><ExperimentTabs /></div>

<div class="matrix-pair">
  <CellGrid :sources="{ 'models-effort': '/models-effort-pairs.json', tests: '/tests-configuration-pairs.json' }" direction="python→javascript" title="Python → TypeScript" />
  <CellGrid :sources="{ 'models-effort': '/models-effort-pairs.json', tests: '/tests-configuration-pairs.json' }" direction="javascript→python" title="TypeScript → Python" />
</div>

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · 12 ports per cell and direction · each grid on its own colour scale · <code>public/models-effort-pairs.json</code>, <code>public/tests-configuration-pairs.json</code> from <code>scripts/pair_metrics.py</code> · 2026-10-29</div>
