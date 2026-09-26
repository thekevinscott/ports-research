# exercise-api

Runs the same `{grammar, input}` cases through the public API of a gbnf reference
and one or more ports of it, in one language, and reports where their outputs differ
and how long each call took. The reference is ground truth; agreement among the ports
themselves falls out as a by-product when more than one target is given.

Per case, a driver calls `GBNF(grammar)`, then `state.add(input)`, then iterates the
resulting state to its rule objects. The driver records `ok`, the error class name and
`pos` when a call raised, the rules normalized to `{type, value}` (so a class instance
and a plain object with the same content compare equal), and wall time in nanoseconds.
Rules are compared as a set.

Ports load the way `execute-test-suite` loads them: python through `PYTHONPATH=<port>`
and `import gbnf`; typescript through `<port>/src/index.ts` and its default export.
`--adapt` applies that package's shim rules (`flat_module` for python, `default_export`
for typescript) to the targets. The reference is never adapted.

## Usage

```
exercise-api --language python \
  --reference ~/.cache/ports/gbnf-experiment/derivations/<key>/source/python \
  --target <run>/ported_implementation --target <run>/ported_implementation \
  --cases cases/generated-seed0-500.jsonl --adapt > report.json
```

Case files are JSONL, one `{"grammar": ..., "input": ...}` per line, with an optional
`rung` label and an optional `repeat` and `warmup` budget. `--repeat` and `--warmup`
are the defaults for cases that carry none; above one timed pass the report gains
per-case `construct_ns` and `add_ns` summaries. A per-case budget exists because the
timeout covers the whole list: without one the slowest case caps how often every
other case can be measured. `cases/ladder.jsonl` uses it — 100 timed passes on the
cases a reference parses in under 100 ms, 5 on the ones costing it seconds, 1 on
nested JSON at depth 8192.

`--out report.json` writes the report there as well as to stdout. While targets are
still running, `report.partial.json` beside it holds the report over the targets
finished so far, rewritten after each one, so an invocation that is killed keeps what
it had. It is removed once the full report is written.

`exercise-api generate --seed 0 --count 500 --out cases.jsonl` writes cases drawn with
hypothesis: grammars from a small GBNF fragment generator (rules, alternatives,
sequences, char classes, repetition, literals; a share of them deliberately invalid) and
inputs that are full valid strings, prefixes, over-runs, or random strings. The same
seed always yields the same file.

`exercise-api fixtures --grammars <tests>/python/iteration/grammars --out cases.jsonl`
turns the reference integration suite's fixture grammars and their input lists into
cases, so coverage of the generated set by the shipped tests is measurable. Both files
for seed 0 / 500 cases and the 453 fixture cases live under `cases/`.

## Output

```
{
  "language": "python",
  "reference": "<dir>",
  "cases": 500,
  "targets": {
    "<dir>": {
      "cases": 500,
      "agree_with_reference": 480,
      "disagree_with_reference": 20,
      "disagreements": [{"case": {...}, "reference": {...}, "target": {...}}, ...],
      "reference_error_cases": 90,
      "target_error_cases": 95,
      "reference_mean_elapsed_ns": ..., "reference_p50_elapsed_ns": ..., "reference_p95_elapsed_ns": ...,
      "target_mean_elapsed_ns": ..., "target_p50_elapsed_ns": ..., "target_p95_elapsed_ns": ...
    }
  },
  "agree_all_targets": 470,
  "agree_all_targets_not_reference": 3
}
```

`disagreements` holds the first 20. The last two keys appear only with more than one
target. A driver that exits non-zero, is killed, or exceeds `--timeout` marks every case
`error_type: "driver_failed"`; one that exits cleanly without answering every case marks
the rest `"driver_exit"`; a port whose entry point cannot be loaded marks every case
`"LoadError"`.

Each driver runs under an address-space cap (`RLIMIT_AS`, `--memory-limit-bytes`),
4 GiB for python and 28 GiB for typescript. The typescript cap is the smallest whole GiB
at which the driver survives on the integration fixture port with a cold tsx compile
cache: at 27 GiB node dies with `WebAssembly.instantiate(): Out of memory`, since V8
reserves virtual space for each wasm memory far beyond what it touches. A warm cache
needs less (26 GiB), which is why a fixed probe can look fine and the test suite not.
