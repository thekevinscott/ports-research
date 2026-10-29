# 2026-10-29T02:53Z — transcript_usage splits on Unicode line separators

`gbnf_experiment.transcript_usage` reads each transcript jsonl with `str.splitlines()`. That splits on U+2028-class separators as well as `\n`, so a record whose text contains one is cut into fragments: the first fails to parse and is skipped, and a later fragment can parse as a bare JSON scalar, where `record.get` raises `AttributeError`.

Observed on run 20261016T112558Z_c9a62987 (v2-models-effort, Opus max, py→ts): a fragment parsed as the int `1` and killed a metrics pass. The quieter effect applies to every run: any assistant record containing such a separator is dropped from the token sum.

Not fixed. The talk's `run_metrics.py` catches the exception and leaves tokens empty for that run. Fix owed in gbnf_experiment with a test: iterate lines with `open()` or split on `\n` only.
