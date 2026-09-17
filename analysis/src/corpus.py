"""Shared corpus selection for the notebook and embedding pair export."""

from pathlib import Path

from dirsql._dirsql import DirSQL

from src.Codebase import Codebase
from src.run_table import completed_runs

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "packages" / "gbnf-experiment" / "data"
REVERSE = ROOT / "proposed-projects" / "round-trip-experiment" / "reverse"
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
EXCLUDE_BY_LANGUAGE = {"python": EXCLUDE, "typescript": [*EXCLUDE, "builder", "dev"]}

def codebases_under(root, table):
    # A fresh DirSQL scan every run, so a run banked since the last refresh is picked up.
    db = DirSQL(str(root), tables=[table])
    return [
        Codebase.from_run(
            row,
            exclude=EXCLUDE_BY_LANGUAGE[row["target_language"]],
            reference=REFERENCE / row["target_language"],
        )
        for row in completed_runs(db, table.name)
    ]

