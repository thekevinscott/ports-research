import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def experiment_data(tmp_path_factory) -> Path:
    """A fresh data tree holding nothing but this session's runs.

    Runs are the session's own, so nothing found there can be an earlier run's.
    """
    return tmp_path_factory.mktemp("data")


@pytest.fixture(scope="session")
def completed_run(experiment_data: Path) -> Path:
    """One real port, driven through the installed entry point. This bills.

    A subprocess rather than CliRunner because settings read the environment at
    import, so redirecting the data directory only holds in a fresh
    interpreter. The command line is the whole public surface of this package,
    and every e2e assertion is made against what it leaves on disk.
    """
    result = subprocess.run(
        ["uv", "run", "run-gbnf-experiment", "--source-language", "typescript"],
        cwd=PACKAGE_ROOT,
        env={
            **os.environ,
            "GBNF_EXPERIMENT_DATA_DIRECTORY": str(experiment_data),
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    [run_directory] = experiment_data.iterdir()
    return run_directory
