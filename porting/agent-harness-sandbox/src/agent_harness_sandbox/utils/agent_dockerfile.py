from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


@contextmanager
def agent_dockerfile(dockerfile: Path, modify: Callable[[str], str] | None) -> Generator[Path]:
    """Yield the Dockerfile to build, writing modified text to a temporary file.

    The temporary file sits outside the build context: `--file` is read by the
    client, so instruction paths still resolve against the context and the
    shipped tree is never written to.
    """
    if modify is None:
        yield dockerfile
        return
    text = modify(dockerfile.read_text())
    with TemporaryDirectory() as tmp_dir:
        modified = Path(tmp_dir) / dockerfile.name
        modified.write_text(text)
        yield modified
