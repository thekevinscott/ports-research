"""The runs banked under --output, read through dirsql. Shared by every study script."""

import asyncio
import subprocess
from functools import cache
from pathlib import Path

import yaml
from dirsql import DirSQL

from gbnf_experiment.condition_name import LABELS

CONDITION = ("source_language", *LABELS, "model", "effort")
ROOT = Path(__file__).resolve().parents[3]


def design(root: Path, study: str) -> dict:
    paths = sorted(root.glob("experiments/*/design.yaml"))
    designs = [d for path in paths if (d := yaml.safe_load(path.read_text()))["study"] == study]
    if len(designs) != 1:
        raise ValueError(f"{len(designs)} designs under {root / 'experiments'} name study {study!r}; expected one")
    return designs[0]


@cache
def is_descendant(root: Path, ancestor: str, commit: str) -> bool:
    merge_base = ["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, commit]
    return subprocess.run(merge_base, capture_output=True).returncode == 0


async def query(data: Path, sql: str) -> list[dict]:
    db = DirSQL(str(data), config=str(data / ".dirsql.toml"), no_ignore=True)
    return await db.query(sql)


def completed_runs(output: Path, study: str, root: Path = ROOT) -> list[dict]:
    """Rows of the runs the study's design counts, from the `runs` table in `.dirsql.toml` beside `output`."""
    spec = design(root, study)
    if not output.is_dir():
        return []
    sql = f"SELECT * FROM runs WHERE study = '{study}' AND harness_commit IS NOT NULL AND {spec['completed_run']}"
    runs = asyncio.run(query(output.parent, sql))
    since = spec["prompt_since"] if isinstance(spec["prompt_since"], list) else [spec["prompt_since"]]
    return [run for run in runs if any(is_descendant(root, str(commit), run["harness_commit"]) for commit in since)]
