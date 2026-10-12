import subprocess
from pathlib import Path

# The gbnf pin: packages/gbnf_experiment/src/gbnf_experiment/config.py `gbnf_commit`.
GBNF_COMMIT = "13f1aca495d11e160fffd68c4ba299a2415909d8"
PATCHES = Path(__file__).resolve().parents[4] / "packages" / "gbnf_experiment" / "docker" / "gbnf-prepare" / "patches"


def clone_reference(directory: Path) -> Path:
    """Clone gbnf at the pin into directory, apply the experiment's patches, and return packages/gbnf."""
    for command in (
        ["init", "-q"],
        ["fetch", "-q", "--depth", "1", "https://github.com/thekevinscott/gbnf", GBNF_COMMIT],
        ["checkout", "-q", "FETCH_HEAD"],
        ["apply", *sorted(str(p) for p in PATCHES.glob("*.patch"))],
    ):
        subprocess.run(["git", "-C", str(directory), *command], check=True)
    return directory / "packages" / "gbnf"
