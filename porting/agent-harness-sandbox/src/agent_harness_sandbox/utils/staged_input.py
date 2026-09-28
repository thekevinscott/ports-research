from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from ..errors import AgentHarnessSandboxError


@contextmanager
def staged_input(input: str | Path) -> Generator[Path]:
    """Yield a throwaway copy of the caller's input folder.

    The copy is what makes /input non-synced: the container can install and
    scratch there, and nothing it writes reaches the caller's folder.
    """
    source = Path(input)
    if not source.exists():
        raise AgentHarnessSandboxError(f"{source} does not exist")
    if not source.is_dir():
        raise AgentHarnessSandboxError(f"{source} is not a directory")

    with TemporaryDirectory() as staging:
        staged = Path(staging) / "input"
        copytree(source, staged, symlinks=True)
        yield staged
