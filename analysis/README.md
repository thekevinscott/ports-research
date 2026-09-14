Marimo notebook over the gbnf-experiment runs in `packages/gbnf-experiment/data` and the
reverse-port runs in `proposed-projects/round-trip-experiment/reverse`. Both tables are
built by a fresh dirsql scan at run time (`src/run_table.py`), so a run banked since the
last refresh appears without a code change.
Edit: `uv run --directory analysis marimo edit runs.py`. Tests: `uv run --directory analysis pytest`.
Charts to disk: `GENERATE_EMBEDDING_BASE_URL=http://127.0.0.1:8089/v1 uv run --directory analysis python export_charts.py`
writes every chart the notebook renders to `charts/` as SVG, PNG and Vega-Lite JSON, built from the notebook's own chart functions.
