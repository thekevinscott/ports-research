"""The runs banked under --output, read through dirsql. Shared by every study script."""

import json
from pathlib import Path

from dirsql import Table

# The package's DirSQL is the async wrapper; the notebook uses the sync binding the same way.
from dirsql._dirsql import DirSQL

from gbnf_experiment.condition_name import LABELS

CONDITION = ("source_language", *LABELS, "model", "effort")
COMPLETED = "exit_code = 0 AND is_error = 0 AND error IS NULL AND completed_at IS NOT NULL"


def run_rows(path: str) -> list[dict]:
    manifest_path = Path(path)
    manifest = json.loads(manifest_path.read_text())
    result_path = manifest_path.parent / "result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else {}
    condition = manifest.get("condition", {})
    return [
        {
            "run_id": manifest_path.parent.name,
            "study": manifest.get("study"),
            "completed_at": manifest.get("completed_at"),
            "exit_code": manifest.get("exit_code"),
            "error": manifest.get("error"),
            "is_error": result.get("is_error"),
            **{key: condition.get(key) for key in CONDITION},
        }
    ]


RUNS = Table(
    name="runs",
    ddl=(
        "CREATE TABLE runs (run_id TEXT PRIMARY KEY, study TEXT, completed_at TEXT, exit_code INTEGER, error TEXT,"
        " is_error INTEGER, source_language TEXT, " + " INTEGER, ".join(LABELS) + " INTEGER, model TEXT, effort TEXT)"
    ),
    glob="*/manifest.json",
    on_file=run_rows,
)


def completed_runs(output: Path, study: str) -> list[dict]:
    """Rows of the study's completed runs; `CONDITION` keys hold the cell, flags as 0/1."""
    if not output.is_dir():
        return []
    db = DirSQL(str(output), tables=[RUNS], no_ignore=True)
    return db.query(f"SELECT * FROM runs WHERE study = '{study}' AND {COMPLETED}")
