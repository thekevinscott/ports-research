from python_on_whales import docker

from .agents.agent import Agent
from .config import BASE_DOCKERFILE, BASE_IMAGE, SANDBOX_DIR


def build_agent_image(*, agent: Agent, debug: bool) -> str:
    """Build the base and the agent's own layer on it, and return the agent's tag.

    Built on every call: the tag is static, so the build is the only step that
    can notice an edited context. A caller that layers its own image on top
    builds after this returns.
    """
    progress = "tty" if debug else False
    docker.build(SANDBOX_DIR, tags=BASE_IMAGE, file=BASE_DOCKERFILE, progress=progress)
    docker.build(SANDBOX_DIR, tags=agent.image, file=agent.dockerfile, progress=progress)
    return agent.image
