<div class="eyebrow">RESULTS · DISTANCE BETWEEN PORTS · DO REPEATS OF ONE SETTING AGREE WITH EACH OTHER?</div>

<div class="tabs-row"><ExperimentTabs /></div>

<div class="matrix-pair">
  <CellGrid :sources="{ 'models-effort': '/models-effort-pairs.json', tests: '/tests-configuration-pairs.json' }" direction="python→javascript" title="Python → TypeScript" />
  <CellGrid :sources="{ 'models-effort': '/models-effort-pairs.json', tests: '/tests-configuration-pairs.json' }" direction="javascript→python" title="TypeScript → Python" />
</div>

<div class="source">models × effort: 4 models × 4 efforts · tests: 8 test conditions, Opus medium · 12 ports per cell and direction · each grid on its own colour scale · <code>public/models-effort-pairs.json</code>, <code>public/tests-configuration-pairs.json</code> from <code>scripts/pair_metrics.py</code> · 2026-10-29</div>
