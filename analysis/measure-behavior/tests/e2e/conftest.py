import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
# The gbnf pin: packages/gbnf_experiment/src/gbnf_experiment/config.py `gbnf_commit`.
GBNF_COMMIT = "13f1aca495d11e160fffd68c4ba299a2415909d8"
PATCHES = PACKAGE_ROOT.parents[1] / "packages" / "gbnf_experiment" / "docker" / "gbnf-prepare" / "patches"


@pytest.fixture(scope="session")
def reference_checkout(tmp_path_factory):
    checkout = tmp_path_factory.mktemp("gbnf")
    for command in (
        ["init", "-q"],
        ["fetch", "-q", "--depth", "1", "https://github.com/thekevinscott/gbnf", GBNF_COMMIT],
        ["checkout", "-q", "FETCH_HEAD"],
        ["apply", *sorted(str(p) for p in PATCHES.glob("*.patch"))],
    ):
        subprocess.run(["git", "-C", str(checkout), *command], check=True)
    return checkout / "packages" / "gbnf"


@pytest.fixture
def run_cli():
    def run(*args):
        return subprocess.run(
            ["uv", "run", "measure-behavior", *[str(arg) for arg in args]],
            cwd=PACKAGE_ROOT,
            capture_output=True,
            text=True,
        )

    return run


@pytest.fixture
def corpus():
    return PACKAGE_ROOT / "corpus"
