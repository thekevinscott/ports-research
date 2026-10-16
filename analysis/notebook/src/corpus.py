"""Shared corpus selection for the notebook and embedding pair export."""

import subprocess
from functools import cache
from itertools import groupby
from operator import itemgetter
from pathlib import Path

import yaml

from dirsql._dirsql import DirSQL

from src.Codebase import REFERENCE_CHECKOUT, Codebase, pinned_reference
from src.run_table import completed_runs, is_v2

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "runs"
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

def design_of(repo, study):
    designs = [
        design
        for path in sorted(Path(repo).glob("experiments/*/design.yaml"))
        if (design := yaml.safe_load(path.read_text()))["study"] == study
    ]
    if len(designs) != 1:
        raise ValueError(f"{len(designs)} designs name study {study!r} under {repo}")
    return designs[0]


@cache
def descends_from(repo, ancestor, commit):
    # Exit 1 is "not an ancestor"; anything else is a commit git does not know, never a quiet exclusion.
    code = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", ancestor, commit]).returncode
    if code not in (0, 1):
        raise ValueError(f"git cannot compare {commit} with {ancestor} in {repo}")
    return code == 0


def under_design(runs, repo, design):
    runs = [
        run
        for run in runs
        if run["harness_commit"] and descends_from(repo, design["prompt_since"], run["harness_commit"])
    ]
    cell = itemgetter("source_language", *(key for key in design["varies"] if key != "source_language"))
    completed = sorted((run for run in runs if run["exit_code"] == 0), key=lambda run: (cell(run), run["completed_at"]))
    kept = {
        run["run_id"]
        for _, cell_runs in groupby(completed, key=cell)
        for run in list(cell_runs)[: design["runs_per_cell"]]
    }
    return [run for run in runs if run["exit_code"] != 0 or run["run_id"] in kept]


def runs_under(root, table, study, *, include_nonzero_exit=False, repo=ROOT):
    """Completed runs under root: every V1 run, and the V2 runs the study's design selects."""
    # A fresh DirSQL scan every run, so a run banked since the last refresh is picked up.
    db = DirSQL(str(root), tables=[table])
    runs = completed_runs(db, table.name, include_nonzero_exit=include_nonzero_exit)
    v2 = [run for run in runs if is_v2(run) and run["study"] == study]
    selected = {run["run_id"] for run in under_design(v2, repo, design_of(repo, study))}
    return [run for run in runs if not is_v2(run) or run["run_id"] in selected]


def codebases_under(root, table, study, *, repo=ROOT):
    pinned_reference()
    return [
        Codebase.from_run(
            row,
            exclude=EXCLUDE_BY_LANGUAGE[row["target_language"]],
            reference=REFERENCE / row["target_language"],
        )
        for row in runs_under(root, table, study, repo=repo)
    ]

