import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
DERIVATION_CACHE = CACHE_HOME / "ports" / "gbnf-experiment" / "derivations"


@pytest.fixture(scope="session")
def experiment_data(tmp_path_factory) -> Path:
    """A fresh data tree holding nothing but this session's runs.

    Runs are the session's own, so nothing found there can be an earlier run's.
    """
    return tmp_path_factory.mktemp("data")


@pytest.fixture(scope="session")
def derivations(tmp_path_factory) -> Path:
    """A path of this session's own onto the real derivation cache.

    Shared rather than fresh: it builds an image and takes minutes, and it is
    keyed by content, so reusing it is what the tool does. Symlinked when the
    cache is already there; when it is not, the run derives into the temp tree
    and this session pays for it once.
    """
    directory = tmp_path_factory.mktemp("cache") / "derivations"
    if DERIVATION_CACHE.is_dir():
        directory.symlink_to(DERIVATION_CACHE)
    return directory


@pytest.fixture(scope="session")
def completed_run(experiment_data: Path, derivations: Path) -> Path:
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
            "GBNF_EXPERIMENT_DERIVATIONS_DIRECTORY": str(derivations),
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    [run_directory] = experiment_data.iterdir()
    return run_directory
