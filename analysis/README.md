Marimo notebook over the gbnf-experiment runs in `packages/gbnf-experiment/data` and the
reverse-port runs in `proposed-projects/round-trip-experiment/reverse`. Both tables are
built by a fresh dirsql scan at run time (`src/run_table.py`), so a run banked since the
last refresh appears without a code change.
Edit: `uv run --directory analysis marimo edit runs.py`. Unit tests: `just --working-directory analysis test-unit`.
Charts to disk: `GENERATE_EMBEDDING_BASE_URL=http://127.0.0.1:8089/v1 uv run --directory analysis python export_charts.py`
writes every chart the notebook renders to `charts/` as SVG, PNG and Vega-Lite JSON, built from the notebook's own chart functions.

Embedding comparisons only: `uv run --directory analysis python export_embedding_pairs.py`.
Validates existing stripped caches against the source, then exports all 380 forward
port pairs (within direction, across conditions) and 40 port/reference comparisons,
cache fingerprints, summary statistics, and charts to `charts/embeddings/`.
Requires the cached vectors and reference sources; no embedding server is needed.
