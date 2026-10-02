from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agent_harness_sandbox.build_agent_image import build_agent_image


@pytest.fixture
def agent():
    return Mock(image="an-agent:latest", stage="an-agent")


@pytest.fixture
def docker():
    with patch("agent_harness_sandbox.build_agent_image.docker", autospec=True) as m:
        yield m


@pytest.fixture
def sandbox_dir():
    with (
        patch("agent_harness_sandbox.build_agent_image.SANDBOX_DIR", Path("/sandbox")),
        patch("agent_harness_sandbox.build_agent_image.DOCKERFILE", Path("/sandbox/Dockerfile")),
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
        assert docker.build.call_count == 2

    def it_never_asks_whether_the_image_is_already_there(build, docker):
        build()
        docker.image.exists.assert_not_called()

    def it_builds_one_image_under_the_agents_tag(build, docker):
        build()
        assert [call.kwargs["tags"] for call in docker.build.call_args_list] == ["an-agent:latest"]

    def it_selects_the_agents_stage(build, docker):
        build()
        assert docker.build.call_args.kwargs["build_args"] == {"AGENT": "an-agent"}

    def it_builds_the_shipped_context_quietly(build, docker, sandbox_dir):
        build()
        assert docker.build.call_args.args == (sandbox_dir,)
        assert docker.build.call_args.kwargs["file"] == Path("/sandbox/Dockerfile")
        assert docker.build.call_args.kwargs["progress"] is False

    def it_streams_build_output_in_debug(build, docker):
        build(debug=True)
        assert docker.build.call_args.kwargs["progress"] == "tty"


SHIPPED_TEXT = "ARG AGENT\nFROM node AS an-agent\nFROM ${AGENT}\n"


def describe_modify_dockerfile():
    @pytest.fixture
    def sandbox_dir(tmp_path):
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(SHIPPED_TEXT)
        with (
            patch("agent_harness_sandbox.build_agent_image.SANDBOX_DIR", tmp_path),
            patch("agent_harness_sandbox.build_agent_image.DOCKERFILE", dockerfile),
        ):
            yield tmp_path

    @pytest.fixture
    def built(docker):
        """The Dockerfile text each build actually saw, in order."""
        texts = []
        docker.build.side_effect = lambda *args, **kwargs: texts.append(Path(kwargs["file"]).read_text())
        return texts

    def describe_when_it_is_not_supplied():
        def it_builds_the_dockerfile_where_it_lies(build, docker, sandbox_dir):
            build()
            assert docker.build.call_args.kwargs["file"] == sandbox_dir / "Dockerfile"

        def it_builds_the_dockerfile_text_unchanged(build, built):
            build()
            assert built == [SHIPPED_TEXT]

    def describe_when_it_is_supplied():
        def it_builds_what_the_callable_returns(build, built):
            build(modify_dockerfile=lambda text: text + "RUN echo modified\n")
            assert built == [SHIPPED_TEXT + "RUN echo modified\n"]

        def it_hands_the_callable_the_whole_dockerfile_text(build):
            seen = []

            def modify(text):
                seen.append(text)
                return text

            build(modify_dockerfile=modify)
            assert seen == [SHIPPED_TEXT]

        def it_still_selects_the_agents_stage(build, docker):
            build(modify_dockerfile=lambda text: text + "RUN echo modified\n")
            assert docker.build.call_args.kwargs["build_args"] == {"AGENT": "an-agent"}

        def it_leaves_the_dockerfile_on_disk_untouched(build, sandbox_dir):
            build(modify_dockerfile=lambda text: "FROM scratch\n")
            assert (sandbox_dir / "Dockerfile").read_text() == SHIPPED_TEXT

        def it_leaves_no_temporary_dockerfile_behind(build, docker):
            paths = []
            docker.build.side_effect = lambda *args, **kwargs: paths.append(Path(kwargs["file"]))
            build(modify_dockerfile=lambda text: text + "RUN echo modified\n")
            assert not paths[0].exists()
