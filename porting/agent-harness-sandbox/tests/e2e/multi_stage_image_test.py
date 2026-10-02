"""The run image really is built in stages, checked against the real daemon.

No model call: the claim is about the image, and it has to be read off the image
rather than from inside a run, because the /input bind mount shadows the image's
own /input for the whole of a run. That shadowing is why the mount goes away in
a later slice; until it does, a mounted run cannot see what the build put there.
"""

import pytest
from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from agent_harness_sandbox.agents.PiAgent import PiAgent
from agent_harness_sandbox.build_agent_image import build_agent_image
from python_on_whales import docker

STAGED_PATH = "/input"
CLIS = {"claude": ClaudeAgent(), "pi": PiAgent(provider="openrouter")}


@pytest.fixture(scope="module", params=CLIS)
def cli(request) -> str:
    return request.param


@pytest.fixture(scope="module")
def image(cli: str) -> str:
    return build_agent_image(agent=CLIS[cli], debug=False)


def probe(image: str, script: str) -> str:
    return docker.run(image, ["sh", "-c", script], entrypoint="", remove=True).strip()


def describe_the_image_the_agent_runs_in():
    def it_carries_the_staged_path_out_of_the_first_stage(image):
        assert probe(image, f"stat -c %U:%F {STAGED_PATH} 2>&1 || true") == "node:directory"

    def it_holds_its_own_agents_cli_and_no_other(image, cli):
        found = probe(image, f"for c in {' '.join(CLIS)}; do command -v $c >/dev/null && echo $c; done; true")
        assert found == cli
