"""Shared corpus selection for the notebook and embedding pair export."""

import os
from pathlib import Path

from dirsql._dirsql import DirSQL

from src.Codebase import REFERENCE_CHECKOUT, Codebase, pinned_reference
from src.run_table import completed_runs, is_v2

ROOT = Path(__file__).resolve().parents[3]
# PORTS_RUNS_DIR points the scan at another runs directory, such as a scratch copy.
DATA = Path(os.environ.get("PORTS_RUNS_DIR", ROOT / "data" / "runs"))
REVERSE = ROOT / "analysis" / "round-trip-experiment" / "reverse"
# The pinned gbnf reference, one package per language.
REFERENCE = REFERENCE_CHECKOUT / "packages" / "gbnf"
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
    "javascript": [*EXCLUDE, "builder", "dev"],
}

def runs_under(root, table, *, include_nonzero_exit=False, study=None):
    """Completed runs under root: every V1 run, and the V2 runs whose manifest names the study (PORTS_STUDY, default v2-test-configurations)."""
    # A fresh DirSQL scan every run, so a run banked since the last refresh is picked up.
    db = DirSQL(str(root), tables=[table])
    runs = completed_runs(db, table.name, include_nonzero_exit=include_nonzero_exit)
    if study is None:
        study = os.environ.get("PORTS_STUDY", "v2-test-configurations")
    return [run for run in runs if not is_v2(run) or run["study"] == study]


def codebases_under(root, table):
    pinned_reference()
    return [
        Codebase.from_run(
            row,
            exclude=EXCLUDE_BY_LANGUAGE[row["target_language"]],
            reference=REFERENCE / row["target_language"],
        )
        for row in runs_under(root, table)
    ]

