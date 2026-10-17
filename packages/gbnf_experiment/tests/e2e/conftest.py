import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def experiment_data(tmp_path_factory) -> Path:
    """A fresh working folder for this session's one run, as the runner gives each run."""
    return tmp_path_factory.mktemp("data")


@pytest.fixture(scope="session")
def completed_run(experiment_data: Path) -> Path:
    """One real port, driven through the installed entry point. This bills.

    Prepares into the real cache: it is keyed by content, so reusing it is what
    the tool does. The command line is the whole public surface of this package,
    and every e2e assertion is made against what it leaves on disk.
    """
    result = subprocess.run(
        [
            "uv", "run", "--project", str(PACKAGE_ROOT), "run_gbnf_experiment",
            "--source-language", "python",
        ],
        cwd=experiment_data,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return experiment_data
