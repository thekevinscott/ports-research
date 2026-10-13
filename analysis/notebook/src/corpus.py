"""Shared corpus selection for the notebook and embedding pair export."""

import os
from pathlib import Path

from dirsql._dirsql import DirSQL

from src.Codebase import Codebase
from src.matrix_run_ids import matrix_run_ids
from src.run_table import completed_runs, is_v2

ROOT = Path(__file__).resolve().parents[3]
# PORTS_RUNS_DIR points the scan at another runs directory, such as a scratch copy.
DATA = Path(os.environ.get("PORTS_RUNS_DIR", ROOT / "data" / "runs"))
REVERSE = ROOT / "analysis" / "round-trip-experiment" / "reverse"
PREPARED = "771a734d60ecbae5"
REFERENCE = Path.home() / ".cache" / "ports" / "gbnf-experiment" / "prepared" / PREPARED / "source"
EXCLUDE = [
    "node_modules",
    "__pycache__",
    ".venv",
    ".pytest_cache",
    "dist",
    "dev-deps",
    "tests",
    "test",
    "integration-tests",
    "conftest.py",
    "*_test.py",
    "test_*.py",
    "*.test.ts",
    "*.spec.ts",
]
EXCLUDE_BY_LANGUAGE = {
    "python": EXCLUDE,
    "typescript": [*EXCLUDE, "builder", "dev"],
    # V2 names its typescript target "javascript".
    "javascript": EXCLUDE,
}

def runs_under(root, table, *, include_nonzero_exit=False, matrices=None):
    """Completed runs under root. Given matrix logs (names under root, or PORTS_MATRICES, comma-separated), V2 runs are only those the logs list; V1 runs are kept."""
    # A fresh DirSQL scan every run, so a run banked since the last refresh is picked up.
    db = DirSQL(str(root), tables=[table])
    runs = completed_runs(db, table.name, include_nonzero_exit=include_nonzero_exit)
    if matrices is None:
        matrices = [name.strip() for name in os.environ.get("PORTS_MATRICES", "").split(",") if name.strip()]
    if not matrices or not any(is_v2(run) for run in runs):
        return runs
    listed = matrix_run_ids(Path(root), matrices)
    return [run for run in runs if not is_v2(run) or run["run_id"] in listed]


def codebases_under(root, table):
    return [
        Codebase.from_run(
            row,
            exclude=EXCLUDE_BY_LANGUAGE[row["target_language"]],
            reference=REFERENCE / row["target_language"],
        )
        for row in runs_under(root, table)
    ]

