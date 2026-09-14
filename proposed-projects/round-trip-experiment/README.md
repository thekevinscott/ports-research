# round-trip-experiment

Tooling for porting a banked port back to its source language and measuring how far
the result lands from the original. Two CLIs: `measure-code-distance` scores two
codebases, `reverse-port` stages and executes the second leg. Only `reverse-port run`
starts a model.

## measure-code-distance

```
measure-code-distance levenshtein --language python|typescript --a <dir> --b <dir> [--exclude PATTERN ...]
measure-code-distance git-diff    --language python|typescript --a <dir> --b <dir> [--exclude PATTERN ...]
```

Two ways of scoring the same pair, both printing one JSON object and both exiting
non-zero with a message on stderr when a directory is missing or has no source files.
`levenshtein` is an edit distance over token, character and path sequences.
`git-diff` normalizes both trees and asks git for the diffstat between them. `--a` is
the reference, `--b` the port.

### levenshtein

Edit distance between two codebases in the same language. Walks each directory
the way `measure-ast` does: `python` reads `*.py`; `typescript` reads `*.ts` with
the typescript grammar and `*.tsx` with the tsx grammar. Each `--exclude` is an
fnmatch pattern applied to the path relative to the directory and to each of its
path parts (the same rule as `analysis/src/Codebase.py::_excluded`). Files are
concatenated in sorted relative-path order. Prints one JSON object; exits non-zero
with a message on stderr when a directory is missing or has no source files.

Every distance is `rapidfuzz.distance.Levenshtein.normalized_distance`: edit
distance divided by the longer of the two sequences, so 0 is identical and 1 is
nothing in common.

- `token_levenshtein`: over tree-sitter leaf tokens with every identifier replaced
  by one placeholder. String and number literals are kept; comments are dropped.
  Python identifiers are `identifier`; typescript also folds `property_identifier`,
  `type_identifier`, the shorthand property identifiers, `private_property_identifier`
  and `statement_identifier`.
- `token_levenshtein_raw`: the same stream with identifiers kept.
- `char_levenshtein`: over the concatenated raw text.
- `path_levenshtein`: over the sorted relative paths of every file (not only sources)
  the excludes keep, each path one token, so it reads as the fraction of the file
  list added, removed, or renamed. `path_count_a`, `path_count_b` are the list lengths.
- `file_count_a`, `file_count_b`, `token_count_a`, `token_count_b`, `char_count_a`,
  `char_count_b`: sizes of what was compared. Token counts are of the abstracted stream.

The gbnf references are about 9-10k tokens and 50k characters, so both codebases go
through rapidfuzz whole; nothing is chunked.

### git-diff

Round-trip fidelity as a diffstat: how many lines a reviewer would have to change to
turn the port back into the hand-written reference in the same language. Both trees
are normalized first, then git does the file matching and the line counting. Nothing
here re-implements either.

The source files each `--exclude` keeps — `*.py`, or `*.ts` and `*.tsx` — are copied
into two scratch directories under `/tmp/claude/`, which are deleted when the command
returns. The originals are never written to. Normalization, identical on both sides:

1. Comments stripped, with `measure-embedding`'s `strip_comments`. `*.tsx` goes
   through the typescript grammar, which the tsx grammar would otherwise own.
2. Blank lines dropped, including the holes a stripped comment leaves behind. Without
   this a comment-heavy port scores worse than an identical one that stays quiet:
   `ruff format` keeps one blank line where a comment block was.
3. Formatted. Python: `ruff format`, then `ruff check --select I --fix` to sort
   imports. Typescript: `pnpm dlx prettier@3.6.2 --write` — prettier does not sort
   imports, so typescript import order still reads as a difference.

A file the formatter refuses is left as it is and listed in `formatter_failures`; it
never fails the run. Failures are found by formatting the tree in one invocation and,
only when that exits non-zero, re-running file by file to say which one it was.

The diffstat comes from `git diff --no-index -M` over the two normalized trees, once
with `--numstat` for the line counts and once with `--name-status -z` for the file
statuses. `-M` is git's own rename detection at its default 50% similarity, so a file
the port moved or renamed is one rename, not an add and a delete.

- `insertions`, `deletions`: lines summed over every `--numstat` row.
- `reference_lines`: lines in the normalized `--a` tree.
- `diff_ratio`: `(insertions + deletions) / reference_lines`. 0 is byte-identical
  after normalization. It is not capped at 1 — a port twice the size of the reference
  scores above it. `null` when the reference normalizes to nothing.
- `similarity_pct`: Dice similarity over lines, `100 * 2 * shared / (reference_lines +
  port_lines)`, where `shared = reference_lines - deletions` and `port_lines = shared +
  insertions`. 100 is byte-identical after normalization, 0 shares no line. Same formula
  as difflib's `SequenceMatcher.ratio`. `null` when both trees normalize to nothing.
- `identical`, `modified`, `renamed`, `added`, `deleted`: file counts. `identical` is
  the files at the same relative path in both trees that git never reported, so
  `identical + modified` is the size of the shared path set.
- `formatter_failures`: `{"side": "a"|"b", "path": ...}` for each file, once per file
  however many of the language's formatter commands rejected it.

## reverse-port

```
reverse-port stage  --run <forward run dir>
reverse-port record --run <reverse run dir> --forward <forward run dir>
reverse-port run    --run <forward run dir>
```

The reverse leg: a banked port goes back through the unmodified harness into the
language it came from, so it can be measured against the original reference in that
language. No file under `packages/gbnf-experiment/` is touched; the harness is reused
by invocation, with the two roots it reads moved by env var. Every path option takes an
existing directory and is resolved absolute.

- **`stage`** copies `<forward run>/ported_implementation/` to
  `~/.cache/ports/round-trip-experiment/derivations/<forward run id>/<derivation cache key>/source/<reverse source language>/`,
  build artefacts (`node_modules`, `__pycache__`, `.venv`, `.pytest_cache`, `dist`) left
  out, and symlinks the real derivation cache's `tests/` beside it. `assemble_reference_implementation`
  cannot tell the staged tree from a derived one. The cache key is gbnf-experiment's own,
  imported from its config. Prints one JSON object — `forward` (the forward run id and its
  condition), `condition` (the reverse one), `staged`, `reverse_root`, `argv`, `env`,
  `estimate` — and starts nothing.
- **`run`** stages, launches `argv` as a subprocess with `env` over the inherited
  environment, then records. The reverse run directory is found by diffing the output root
  around the launch, because the harness prints its path only when the run succeeds; a
  failed leg is banked and joined back all the same. Prints the stage report plus
  `run_directory` and `returncode`, and exits with the harness's own status.
- **`record`** re-reads the `manifest.json` the harness wrote and adds one key,
  `forward: {"run_id": ..., "condition": {...}}`, taken from the forward run's own
  manifest. The harness's keys and its two-space formatting are left as they were. `run`
  does this itself; the subcommand is for a leg whose recording did not happen.

`estimate` is the forward leg's own numbers standing in for the second: `total_tokens` and
`api_calls` summed over the forward transcript's API calls (prompt and output, cache reads
and writes counted at full weight, the same sum `analysis/runs.py` reports) and `duration_ms`
from its `result.json`. No cost in dollars is computed.

Staging is checked before the invocation is built, so `stage` and `run` both refuse an
incomplete derivation: `source/<language>/` and a `tests/<language>/` for each included
suite have to exist and be non-empty. A missing cache-key directory reads as a cache miss to
`PreparedFilesystem`, which would silently derive the real gbnf reference into it — a
twenty-minute docker build against the wrong input.

Two env assignments over the inherited environment are the whole redirection:
`GBNF_EXPERIMENT_DERIVATIONS_DIRECTORY=<staging>/<forward run id>`, whose one entry is the
staged port under the harness's own cache key, and
`GBNF_EXPERIMENT_DATA_DIRECTORY=<reverse>/<forward run id>` for the output.

The reverse condition is constant, whatever the forward cell was: the port is the source,
the language is the one the forward run started from, both suites are included
(`--include-typescript-tests --include-python-tests`), and `--effort` and `--model` are
the forward run's own. Constant, so reverse output measures the forward port rather than
the reverse arm. `condition.name` on a reverse manifest is therefore indistinguishable
from a forward one — the output path and the `forward` key are the discriminators.

Output layout, one root per forward run so a leg is findable whatever its exit status:

```
reverse/<forward run id>/<YYYYmmddTHHMMSSZ_xxxxxxxx>/   # ported_implementation/, transcript/, manifest.json, result.json
```

`ROUND_TRIP_EXPERIMENT_REVERSE_DIRECTORY` (default `reverse/` here, tracked in git) moves that
root; `ROUND_TRIP_EXPERIMENT_STAGING_DIRECTORY` (default
`~/.cache/ports/round-trip-experiment/derivations`) moves the staged derivations, which are
a cache and can be trashed once a leg is banked.

## Tests

`just test-unit`, `just test-integration`, `just test-e2e`. Integration drives the CLIs as
subprocesses over fixture directories under `tmp_path`; for `reverse-port run` the harness
is a stub first on `PATH`, so the tier launches no container and starts no model. E2e drives
them over the derived gbnf references in `~/.cache` and the first completed run under
`packages/gbnf-experiment/data`, and skips when either is absent. A billed e2e reverse leg
is deliberately absent until the pilot is approved.
