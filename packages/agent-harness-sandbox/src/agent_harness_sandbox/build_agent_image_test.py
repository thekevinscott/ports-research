from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agent_harness_sandbox.build_agent_image import build_agent_image


@pytest.fixture
def agent():
    return Mock(image="an-agent:latest", dockerfile=Path("/sandbox/Dockerfile.an-agent"))


@pytest.fixture
def docker():
    with patch("agent_harness_sandbox.build_agent_image.docker", autospec=True) as m:
        yield m


@pytest.fixture
def sandbox_dir():
    with (
        patch("agent_harness_sandbox.build_agent_image.SANDBOX_DIR", Path("/sandbox")),
        patch("agent_harness_sandbox.build_agent_image.BASE_DOCKERFILE", Path("/sandbox/Dockerfile")),
    ):
        yield Path("/sandbox")


@pytest.fixture
def build(docker, sandbox_dir, agent):
    def call(**overrides):
        return build_agent_image(**{"agent": agent, "debug": False, **overrides})

    return call


def describe_build_agent_image():
    def it_returns_the_agents_image_tag(build):
        assert build() == "an-agent:latest"

    def it_takes_its_options_by_keyword_only(agent):
        with pytest.raises(TypeError):
            build_agent_image(agent, False)

    def it_builds_every_time(build, docker):
        """A static tag makes the build the only thing that can notice an edited context."""
        build()
        build()
        assert docker.build.call_count == 4

    def it_never_asks_whether_the_image_is_already_there(build, docker):
        build()
        docker.image.exists.assert_not_called()

    def it_builds_the_base_before_the_agent_layer(build, docker):
        build()
        assert [call.kwargs["tags"] for call in docker.build.call_args_list] == [
            "agent-harness-sandbox-base:latest",
            "an-agent:latest",
        ]

    def it_builds_the_shipped_context_quietly(build, docker, sandbox_dir):
        build()
        assert [call.args for call in docker.build.call_args_list] == [(sandbox_dir,), (sandbox_dir,)]
        assert [call.kwargs["file"] for call in docker.build.call_args_list] == [
            Path("/sandbox/Dockerfile"),
            Path("/sandbox/Dockerfile.an-agent"),
        ]
        assert [call.kwargs["progress"] for call in docker.build.call_args_list] == [False, False]

    def it_streams_build_output_in_debug(build, docker):
        build(debug=True)
        assert docker.build.call_args.kwargs["progress"] == "tty"
