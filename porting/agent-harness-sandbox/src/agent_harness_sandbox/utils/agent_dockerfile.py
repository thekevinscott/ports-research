from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from ..agents.agent import Agent


@contextmanager
def agent_dockerfile(agent: Agent, modify: Callable[[str], str] | None) -> Generator[Path]:
    """Yield the Dockerfile to build, writing modified text to a temporary file.

    The temporary file sits outside the build context: `--file` is read by the
    client, so instruction paths still resolve against the context and the
    shipped tree is never written to.
    """
    if modify is None:
        yield agent.dockerfile
        return
    text = modify(agent.dockerfile.read_text())
    with TemporaryDirectory() as tmp_dir:
        dockerfile = Path(tmp_dir) / agent.dockerfile.name
        dockerfile.write_text(text)
        yield dockerfile
