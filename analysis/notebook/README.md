Marimo notebook over the gbnf-experiment runs in `data/runs` and the
reverse-port runs in `analysis/round-trip-experiment/reverse`. Both tables are
built by a fresh dirsql scan at run time (`src/run_table.py`), so a run banked since the
last refresh appears without a code change.

The run table reads V1 manifests (`include_python_tests`, `include_typescript_tests`) and V2 manifests (`include_unit_tests`, `include_source_integration_tests`, `include_target_integration_tests`, `exit_code`); a row carries one set and nulls for the other. V2 runs that exited non-zero are dropped unless `completed_runs` is called with `include_nonzero_exit=True`, which also keeps a killed run that wrote no result. `terminal_reason` comes from the result (`api_error` on an API failure). The existing sections measure V1 runs only. `PORTS_RUNS_DIR` points the scan at another runs directory.

The held-out behavior section measures V2 runs only: measure-behavior runs each port over its corpus (100 generated grammars, 799 inputs) and compares the outcomes with the reference's, cached under `~/.cache/ports/analysis/codebases/behavior/` by the port's contents. Uncached, a python port takes about 22 s and a javascript port about 105 s.

The held-out API section measures V2 runs only: measure-api runs each port over its corpus (100 generated grammars, 999 cases) and compares the outcomes with the reference's, cached under `~/.cache/ports/analysis/codebases/api/` by the port's contents. Uncached, a python port takes about 38 s and a javascript port about 168 s.

The V2 statistics section reads V2 runs only: n, median and IQR per cell, failures per cell, a per-flag permutation and bootstrap comparison, and Spearman rank correlations. The arithmetic is in `src/stats.py` (numpy only).

Edit: `uv run --directory analysis/notebook marimo edit runs.py`. Unit tests: `just --working-directory analysis/notebook test-unit`.
Charts to disk: `GENERATE_EMBEDDING_BASE_URL=http://127.0.0.1:8089/v1 uv run --directory analysis/notebook python export_charts.py`
writes every chart the notebook renders to `charts/` as SVG, PNG and Vega-Lite JSON, built from the notebook's own chart functions.

Embedding comparisons only: `uv run --directory analysis/notebook python export_embedding_pairs.py`.
Validates existing stripped caches against the source, then exports all 380 forward
port pairs (within direction, across conditions) and 40 port/reference comparisons,
cache fingerprints, summary statistics, and charts to `charts/embeddings/`.
Requires the cached vectors and reference sources; no embedding server is needed.
