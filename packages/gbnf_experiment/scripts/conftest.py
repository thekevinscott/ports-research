import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

DIRSQL_CONFIG = Path(__file__).resolve().parents[3] / "data" / ".dirsql.toml"
COMPLETED_RUN = "exit_code = 0 AND is_error = 0 AND error IS NULL AND completed_at IS NOT NULL"


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture(autouse=True)
def dirsql_config(tmp_path):
    """The committed runs table, beside the tests' `tmp_path / "runs"`."""
    shutil.copy(DIRSQL_CONFIG, tmp_path / ".dirsql.toml")


@pytest.fixture
def repo(tmp_path) -> tuple[Path, dict[str, str]]:
    """A repo whose history is before -> since -> after; returns its root and each commit."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    commits = {}
    for name in ("before", "since", "after"):
        git(root, "commit", "-q", "--allow-empty", "-m", name)
        commits[name] = git(root, "rev-parse", "HEAD")
    return root, commits


def write_design(root: Path, name: str, study: str, prompt_since: str, completed_run: str = COMPLETED_RUN) -> None:
    directory = root / "experiments" / name
    directory.mkdir(parents=True)
    design = {"study": study, "runs_per_cell": 12, "completed_run": completed_run, "prompt_since": prompt_since}
    (directory / "design.yaml").write_text(yaml.safe_dump(design))
