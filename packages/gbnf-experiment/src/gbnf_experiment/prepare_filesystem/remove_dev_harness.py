import shutil
from pathlib import Path

DEV_HARNESS_DIRECTORIES = {"typescript": "dev"}


def remove_dev_harness(*, directory: Path, language: str) -> None:
    """Delete the language's dev harness from beside the library being ported.

    The typescript reference ships browser and node demo apps under dev/, each
    with its own package.json and vite config. They are tooling for developing
    the library, not the library, so the container is not shown them. Python has
    no equivalent; dev-deps/ there is dependency pinning and is left alone.
    """
    harness = DEV_HARNESS_DIRECTORIES.get(language)
    if harness and (directory / harness).is_dir():
        shutil.rmtree(directory / harness)
