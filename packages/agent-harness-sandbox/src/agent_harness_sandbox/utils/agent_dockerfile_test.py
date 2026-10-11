from dataclasses import dataclass
from pathlib import Path

import pytest

from agent_harness_sandbox.utils.agent_dockerfile import agent_dockerfile


@dataclass
class StubAgent:
    """Stands in for the package's agent type: only its dockerfile is read."""

    dockerfile: Path


@pytest.fixture
def agent(tmp_path):
    dockerfile = tmp_path / "Dockerfile.stub"
    dockerfile.write_text("FROM base\n")
    return StubAgent(dockerfile=dockerfile)


def describe_agent_dockerfile():
    def describe_when_modify_is_none():
        def it_yields_the_agents_own_dockerfile(agent):
            with agent_dockerfile(agent, None) as dockerfile:
                assert dockerfile == agent.dockerfile

    def describe_when_modify_is_supplied():
        def it_hands_over_the_dockerfiles_text(agent):
            seen = []
            with agent_dockerfile(agent, lambda text: seen.append(text) or text):
                pass
            assert seen == ["FROM base\n"]

        def it_yields_a_file_holding_what_modify_returned(agent):
            with agent_dockerfile(agent, lambda _: "FROM other\n") as dockerfile:
                assert dockerfile.read_text() == "FROM other\n"

        def it_keeps_the_dockerfiles_name(agent):
            with agent_dockerfile(agent, lambda text: text) as dockerfile:
                assert dockerfile.name == "Dockerfile.stub"

        def it_yields_a_file_outside_the_agents_directory(agent):
            with agent_dockerfile(agent, lambda text: text) as dockerfile:
                assert dockerfile.parent != agent.dockerfile.parent

        def it_leaves_the_dockerfile_on_disk_untouched(agent):
            with agent_dockerfile(agent, lambda _: "FROM other\n"):
                pass
            assert agent.dockerfile.read_text() == "FROM base\n"

        def it_discards_the_temporary_file_when_the_block_ends(agent):
            with agent_dockerfile(agent, lambda text: text) as dockerfile:
                written = dockerfile
            assert not written.exists()
