"""The runs banked under --output, read through dirsql. Shared by every study script."""

import json
import subprocess
from functools import cache
from pathlib import Path

import yaml
from dirsql import Table

# The package's DirSQL is the async wrapper; the notebook uses the sync binding the same way.
from dirsql._dirsql import DirSQL

from gbnf_experiment.condition_name import LABELS

CONDITION = ("source_language", *LABELS, "model", "effort")
ROOT = Path(__file__).resolve().parents[3]


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
            "harness_commit": manifest.get("harness", {}).get("commit"),
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
        "CREATE TABLE runs (run_id TEXT PRIMARY KEY, study TEXT, harness_commit TEXT, completed_at TEXT, exit_code INTEGER, error TEXT,"
        " is_error INTEGER, source_language TEXT, " + " INTEGER, ".join(LABELS) + " INTEGER, model TEXT, effort TEXT)"
    ),
    glob="*/manifest.json",
    on_file=run_rows,
)


def design(root: Path, study: str) -> dict:
    designs = [d for path in sorted(root.glob("experiments/*/design.yaml")) if (d := yaml.safe_load(path.read_text()))["study"] == study]
    if len(designs) != 1:
        raise ValueError(f"{len(designs)} designs under {root / 'experiments'} name study {study!r}; expected one")
    return designs[0]


@cache
def is_descendant(root: Path, ancestor: str, commit: str) -> bool:
    return subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, commit], capture_output=True).returncode == 0


def completed_runs(output: Path, study: str, root: Path = ROOT) -> list[dict]:
    """Rows of the runs the study's design counts; `CONDITION` keys hold the cell, flags as 0/1."""
    spec = design(root, study)
    if not output.is_dir():
        return []
    db = DirSQL(str(output), tables=[RUNS], no_ignore=True)
    runs = db.query(f"SELECT * FROM runs WHERE study = '{study}' AND harness_commit IS NOT NULL AND {spec['completed_run']}")
    return [run for run in runs if is_descendant(root, str(spec["prompt_since"]), run["harness_commit"])]
