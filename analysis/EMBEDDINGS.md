# Embedding normalization

What happens to a codebase before it becomes a vector, for the embedding
distances in `runs.py` ("## Embeddings"). Implementation lives in
`proposed-projects/measure-embedding/`; the analysis drives it from
`analysis/src/Codebase.py`.

## File selection

Only source files are embedded: `.py` for Python, `.ts`/`.tsx` for
TypeScript. Everything else is excluded before normalization:

- build/dependency dirs: `node_modules`, `__pycache__`, `.venv`,
  `.pytest_cache`, `dist`, `dev-deps`
- tests: `tests`, `test`, `integration-tests`, `conftest.py`,
  `*_test.py`, `test_*.py`, `*.test.ts`, `*.spec.ts`
- TypeScript ports additionally exclude `builder/` and `dev/`

(`EXCLUDE_BY_LANGUAGE` in `analysis/runs.py`; walk in
`collect_files.py`.)

## Normalization

One step, and one step only: **comments are stripped**. Both sides —
port and hand-written reference — go through the identical transform
(`--strip-comments` is passed on every `embed` call).

Stripping is syntactic, not textual: the source is parsed with
tree-sitter (`tree_sitter_python` / `tree_sitter_typescript`), every
`comment` node's byte span is cut, and the remaining bytes are
concatenated verbatim (`strip_comments.py`). The stripped text is
written beside the output vector as `<file>.stripped`, so exactly what
the model saw is inspectable.

Deliberately **not** done — the contrast with the `git diff` measures,
which do all of this:

- no formatting normalization (no `ruff format`, no `prettier`)
- no blank-line removal
- no import sorting
- no identifier normalization

The only thing standing between the raw file and the embedding model is
comment removal.

## Embedding

- Model: `qwen3-embedding-0.6b-q8_0`, 8192-token context. The largest
  source file is 10,356 bytes, so nothing is truncated.
- One vector per file; vectors are cached under
  `~/.cache/ports/analysis/embeddings-stripped/` keyed by run, with
  mtime-based staleness.

## Comparison

Vectors are L2-normalized to unit length (`load_unit_rows`), so the dot
product is cosine similarity. Per port/reference pair
(`compare_embeddings.py`, `chamfer_distance.py`):

- `chamfer_a_to_b`: for each port file, cosine distance to its nearest
  reference file, averaged with weights equal to the **stripped** file
  lengths in bytes.
- `chamfer_b_to_a`: the same walk from the reference's side.
- `chamfer_distance`: the mean of the two. This is the headline number.
- Also reported: `mean_cosine_distance` (distance between the mean
  vectors) and `mean_nearest_file_distance` (unweighted).

Ports are compared only against the hand-written reference in the same
language — port on `a`, reference on `b`.

## Calibration

The same measure taken on 2026-09-10 against mutated copies of the
references themselves, as a scale:

| mutation | python | typescript |
| --- | --- | --- |
| unchanged copy | 0.000 | 0.000 |
| every definition reordered | 0.010 | 0.005 |
| 10% of files deleted | 0.023 | 0.004 |
| every identifier renamed | 0.030 | 0.024 |
| renamed and reordered | 0.039 | 0.027 |
| 25% of files deleted | 0.043 | 0.022 |
| renamed, reordered, 10% deleted | 0.063 | 0.031 |

The dashed rules on the `chamfer_distance` panels in the notebook are
these six rungs, drawn at the value for the panel's language.

A consistent rename costs as much as deleting a quarter of the files, so
this embedder is largely measuring vocabulary, and the number cannot
tell "every file slightly different" from "most files exact and a few
unrelated". Read it as a relative distance between ports, not a fidelity
grade.
