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


BASE_TEXT = "FROM python:3.13-slim\n"
AGENT_TEXT = "FROM agent-harness-sandbox-base:latest\nCOPY entrypoint.sh /entrypoint.sh\n"


def describe_modify_dockerfile():
    @pytest.fixture
    def sandbox_dir(tmp_path):
        base = tmp_path / "Dockerfile"
        base.write_text(BASE_TEXT)
        with (
            patch("agent_harness_sandbox.build_agent_image.SANDBOX_DIR", tmp_path),
            patch("agent_harness_sandbox.build_agent_image.BASE_DOCKERFILE", base),
        ):
            yield tmp_path

    @pytest.fixture
    def agent(tmp_path):
        dockerfile = tmp_path / "Dockerfile.an-agent"
        dockerfile.write_text(AGENT_TEXT)
        return Mock(image="an-agent:latest", dockerfile=dockerfile)

    @pytest.fixture
    def built(docker):
        """The Dockerfile text each build actually saw, in order."""
        texts = []
        docker.build.side_effect = lambda *args, **kwargs: texts.append(Path(kwargs["file"]).read_text())
        return texts

    def describe_when_it_is_not_supplied():
        def it_builds_the_agent_dockerfile_where_it_lies(build, docker, agent):
            build()
            assert docker.build.call_args.kwargs["file"] == agent.dockerfile

        def it_builds_the_agent_dockerfile_text_unchanged(build, built):
            build()
            assert built == [BASE_TEXT, AGENT_TEXT]

    def describe_when_it_is_supplied():
        def it_builds_what_the_callable_returns(build, built):
            build(modify_dockerfile=lambda text: text + "RUN echo modified\n")
            assert built[1] == AGENT_TEXT + "RUN echo modified\n"

        def it_hands_the_callable_the_agent_dockerfile_text(build):
            seen = []

            def modify(text):
                seen.append(text)
                return text

            build(modify_dockerfile=modify)
            assert seen == [AGENT_TEXT]

        def it_leaves_the_base_dockerfile_alone(build, built):
            build(modify_dockerfile=lambda text: "FROM scratch\n")
            assert built[0] == BASE_TEXT

        def it_leaves_the_agent_dockerfile_on_disk_untouched(build, agent):
            build(modify_dockerfile=lambda text: "FROM scratch\n")
            assert agent.dockerfile.read_text() == AGENT_TEXT

        def it_leaves_no_temporary_dockerfile_behind(build, docker):
            paths = []
            docker.build.side_effect = lambda *args, **kwargs: paths.append(Path(kwargs["file"]))
            build(modify_dockerfile=lambda text: text + "RUN echo modified\n")
            assert not paths[1].exists()
