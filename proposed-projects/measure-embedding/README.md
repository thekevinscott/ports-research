# measure-embedding

Projects a source tree into an embedding space, one vector per file, and
measures cosine distance between two projected trees.

## Usage

```
measure-embedding embed --language python|typescript --target <dir> --out <dir> --model <name> [--exclude PATTERN ...] [--strip-comments]
measure-embedding compare --a <embeddings dir> --b <embeddings dir>
```

`embed` walks `<target>` recursively. `python` embeds `*.py`; `typescript`
embeds `*.ts` and `*.tsx`. Each `--exclude` is an fnmatch pattern applied to
the path relative to `<target>` and to each of its path parts; a file is
skipped when any candidate matches any pattern. Every counted file is embedded
through `packages/generate-embedding` (so `GENERATE_EMBEDDING_BASE_URL`, and
optionally `GENERATE_EMBEDDING_API_KEY`, must be set) and written to
`<out>/<relative/path>.npy` as float32. A file whose `.npy` already exists and
is newer than the source is not re-embedded. With `--strip-comments` every
`comment` node is deleted from the file's tree-sitter parse and the remaining
text — layout otherwise untouched — is written to
`<out>/<relative/path>.stripped` and embedded instead of the source.
`<out>/index.json` records `language`, `target`, `model`, `dims`, the `files`
embedded, in path order, and their `lengths` in characters of the text that was
embedded. Prints that index plus `embedded` and `skipped` counts as JSON. Exits
non-zero when no file was counted or the embedder fails.

`compare` reads both `index.json` files and their vectors, unit-normalises
every row, and prints JSON:

- `mean_cosine_distance`: cosine distance (1 minus cosine similarity) between
  the two centroids.
- `mean_nearest_file_distance`: for each file in `a`, the cosine distance to
  its nearest file in `b`, averaged over `a`.
- `chamfer_a_to_b`: for each file in `a`, the cosine distance to its nearest
  file in `b`, averaged over `a` weighted by the `lengths` in `a`'s index.
- `chamfer_b_to_a`: the same from `b`'s side.
- `chamfer_distance`: the mean of the two directions.
- `file_count_a`, `file_count_b`.

Exits non-zero when the two indexes have different `dims`.
