import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from python_on_whales import docker

from .agents.agent import Agent
from .config import BASE_DOCKERFILE, BASE_IMAGE, SANDBOX_DIR


def build_agent_image(*, agent: Agent, modify_dockerfile: Callable[[str], str] | None = None, debug: bool) -> str:
    """Build the base and the agent's own layer on it, and return the agent's tag.

    `modify_dockerfile` takes the agent Dockerfile's text and returns the text to
    build, so a caller can extend the agent layer without editing the shipped
    file. `None` builds the file as it lies.

    Built on every call: the tag is static, so the build is the only step that
    can notice an edited context. A caller that layers its own image on top
    builds after this returns.
    """
    progress = "tty" if debug else False
    docker.build(SANDBOX_DIR, tags=BASE_IMAGE, file=BASE_DOCKERFILE, progress=progress)
    with _agent_dockerfile(agent, modify_dockerfile) as dockerfile:
        docker.build(SANDBOX_DIR, tags=agent.image, file=dockerfile, progress=progress)
    return agent.image


@contextmanager
def _agent_dockerfile(agent: Agent, modify_dockerfile: Callable[[str], str] | None) -> Iterator[Path]:
    """Yield the Dockerfile to build, writing modified text to a temporary file.

    The temporary file sits outside SANDBOX_DIR, which stays the build context:
    `--file` is read by the client, so instruction paths still resolve against
    the context and the shipped tree is never written to.
    """
    if modify_dockerfile is None:
        yield agent.dockerfile
        return
    text = modify_dockerfile(agent.dockerfile.read_text())
    with tempfile.TemporaryDirectory() as tmp_dir:
        dockerfile = Path(tmp_dir) / agent.dockerfile.name
        dockerfile.write_text(text)
        yield dockerfile
