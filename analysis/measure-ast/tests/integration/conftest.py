import subprocess

import pytest

# The gbnf pin: packages/gbnf_experiment/src/gbnf_experiment/config.py `gbnf_commit`.
GBNF_COMMIT = "13f1aca495d11e160fffd68c4ba299a2415909d8"


@pytest.fixture(scope="session")
def python_reference(tmp_path_factory):
    # The gbnf-prepare patches touch only the javascript package, so the python tree needs none.
    checkout = tmp_path_factory.mktemp("gbnf").resolve()
    for command in (
        ["init", "-q"],
        ["fetch", "-q", "--depth", "1", "https://github.com/thekevinscott/gbnf", GBNF_COMMIT],
        ["checkout", "-q", "FETCH_HEAD"],
    ):
        subprocess.run(["git", "-C", str(checkout), *command], check=True)
    return checkout / "packages" / "gbnf" / "python"
