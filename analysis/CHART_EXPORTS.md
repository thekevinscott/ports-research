# Chart exports

`export_charts.py` writes the existing light SVG, PNG and Vega-Lite JSON plus a
`<name>-dark.svg` beside each chart. This applies to every chart yielded by the
notebook exporter, including future `port-to-port-grid-*` charts.

The shared implementation is `src/chart_export.py`. Dark SVGs are rendered from
a copy of the Vega-Lite spec with transparent background and dark theme colors.
Data, layout and categorical palettes are preserved. Matrix quantitative color
scales use a ramp from `#161513` to the existing deep blue `#0d366b`.

To regenerate dark SVGs from saved specs without running the notebook or its
embedding work, run from `analysis/`:

```sh
uv run python -m src.chart_export charts/statistical-analysis/size-*.json charts/performance/ladder-ref-ratio-*.json charts/statistical-analysis/port-to-port-matrix-*.json
```

Validation: `just test-unit`.
