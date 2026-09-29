"""The run image really is built in stages, checked against the real daemon.

No model call: the claim is about the image, and it has to be read off the image
rather than from inside a run, because the /input bind mount shadows the image's
own /input for the whole of a run. That shadowing is why the mount goes away in
a later slice; until it does, a mounted run cannot see what the build put there.
"""

import pytest
from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from agent_harness_sandbox.build_agent_image import build_agent_image
from python_on_whales import docker

STAGED_PATH = "/input"


@pytest.fixture(scope="module")
def image() -> str:
    return build_agent_image(agent=ClaudeAgent(), debug=False)


@pytest.fixture(scope="module")
def staged(image: str) -> str:
    """Owner and type of the staged path, read off the built image."""
    probe = f"stat -c %U:%F {STAGED_PATH} 2>&1 || true"
    return docker.run(image, ["sh", "-c", probe], entrypoint="", remove=True).strip()


def describe_the_image_the_agent_runs_in():
    def it_carries_the_staged_path_out_of_the_first_stage(staged):
        assert staged == "node:directory"
