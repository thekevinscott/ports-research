from collections.abc import Callable

from python_on_whales import docker

from .agents.agent import Agent
from .config import DOCKERFILE, SANDBOX_DIR
from .utils.agent_dockerfile import agent_dockerfile


def build_agent_image(*, agent: Agent, modify_dockerfile: Callable[[str], str] | None = None, debug: bool) -> str:
    """Build the agent's stage of the sandbox Dockerfile, and return the agent's tag.

    `modify_dockerfile` takes the Dockerfile's text and returns the text to
    build, so a caller can extend the image without editing the shipped file.
    `None` builds the file as it lies.

    Built on every call: the tag is static, so the build is the only step that
    can notice an edited context. A caller that layers its own image on top
    builds after this returns.
    """
    with agent_dockerfile(DOCKERFILE, modify_dockerfile) as dockerfile:
        docker.build(
            SANDBOX_DIR,
            tags=agent.image,
            file=dockerfile,
            build_args={"AGENT": agent.stage},
            progress="tty" if debug else False,
        )
    return agent.image
