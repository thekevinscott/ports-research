"""Load Claude session transcript records from disk.

A transcript is a JSON-lines file: one JSON object per line, each a record
emitted by the Claude Code session logger. A run's transcripts may be split
across several `.jsonl` files under one `transcript/` tree, so the loader
accepts either a single file or a directory (in which case it reads every
`.jsonl` file beneath it, in sorted order, and concatenates their records).

Blank lines are skipped. A line that fails to parse is kept as a ``raw``
record rather than dropped, so the viewer never silently hides evidence: a
malformed line shows up in the page instead of vanishing.
"""

from __future__ import annotations

import json
from pathlib import Path

__all__ = ["load_records", "Record"]


type Record = dict


def load_records(path: Path) -> list[Record]:
    """Read transcript records from ``path``.

    ``path`` may be a single ``.jsonl`` file or a directory. Directory input
    reads every ``.jsonl`` file under it recursively, sorted by path so the
    order is deterministic across machines.
    """
    if path.is_dir():
        files = sorted(path.rglob("*.jsonl"))
        records: list[Record] = []
        for file in files:
            records.extend(_read_file(file))
        return records
    return _read_file(path)


def _read_file(path: Path) -> list[Record]:
    records: list[Record] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            # Keep unparseable lines visible instead of dropping them silently.
            records.append({"type": "raw", "line": line})
    return records
