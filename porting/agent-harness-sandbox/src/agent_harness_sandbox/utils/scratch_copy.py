from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from ..errors import AgentHarnessSandboxError


@contextmanager
def scratch_copy(folder: str | Path) -> Generator[Path]:
    """Yield a throwaway copy of a folder, discarded when the block ends.

    Mounting the copy is what makes /input non-synced: the container can install
    and scratch there, and nothing it writes reaches the caller's folder.
    """
    source = Path(folder)
    if not source.exists():
        raise AgentHarnessSandboxError(f"{source} does not exist")
    if not source.is_dir():
        raise AgentHarnessSandboxError(f"{source} is not a directory")

    with TemporaryDirectory() as scratch:
        copy = Path(scratch) / source.name
        copytree(source, copy, symlinks=True)
        yield copy
