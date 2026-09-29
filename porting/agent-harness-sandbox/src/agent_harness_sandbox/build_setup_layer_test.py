from pathlib import Path
from unittest.mock import patch

import pytest

from agent_harness_sandbox.build_setup_layer import build_setup_layer
from agent_harness_sandbox.errors import AgentHarnessSandboxError

BASE_IMAGE = "an-agent:latest"


@pytest.fixture
def builds() -> list[dict]:
    return []


@pytest.fixture
def docker(builds):
    with patch("agent_harness_sandbox.build_setup_layer.docker", autospec=True) as m:

        def record_build(context, tags, file, **options):
            context = Path(context)
            builds.append(
                {
                    "tags": tags,
                    "dockerfile": Path(file).read_text(),
                    "files": {p.name: p.read_text() for p in context.iterdir()},
                    "options": options,
                }
            )

        m.build.side_effect = record_build
        yield m


@pytest.fixture
def setup_script(tmp_path: Path) -> Path:
    script = tmp_path / "setup.sh"
    script.write_text("#!/bin/sh\nnpm install -g something\n")
    return script


@pytest.fixture
def build(docker, setup_script):
    def call(**overrides):
        return build_setup_layer(**{"base_image": BASE_IMAGE, "setup_script": setup_script, "debug": False, **overrides})

    return call


def describe_build_setup_layer():
    def it_returns_a_tag_distinct_from_the_base_image(build):
        assert build() != BASE_IMAGE

    def it_takes_its_options_by_keyword_only(setup_script):
        with pytest.raises(TypeError):
            build_setup_layer(BASE_IMAGE, setup_script, False)

    def it_builds_once(build, docker):
        build()
        assert docker.build.call_count == 1

    def it_builds_a_layer_on_top_of_the_base_image(build, builds):
        build()
        [call] = builds
        assert call["dockerfile"].splitlines()[0] == f"FROM {BASE_IMAGE}"

    def it_copies_the_setup_script_into_the_build_context_and_runs_it(build, builds):
        build()
        [call] = builds
        assert call["files"]["setup.sh"] == "#!/bin/sh\nnpm install -g something\n"
        assert "setup.sh" in call["dockerfile"]
        assert "RUN" in call["dockerfile"]

    def it_drops_setuid_bits_picked_up_while_running_as_root(build, builds):
        build()
        [call] = builds
        assert "chmod a-s" in call["dockerfile"]

    def it_ends_back_on_the_unprivileged_user(build, builds):
        build()
        [call] = builds
        lines = [line.strip() for line in call["dockerfile"].splitlines() if line.strip()]
        assert lines[-1] == "USER node"

    def it_streams_build_output_in_debug(build, docker):
        build(debug=True)
        assert docker.build.call_args.kwargs["progress"] == "tty"

    def it_is_quiet_by_default(build, docker):
        build()
        assert docker.build.call_args.kwargs["progress"] is False

    def it_refuses_a_setup_script_that_does_not_exist(tmp_path, docker):
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            build_setup_layer(base_image=BASE_IMAGE, setup_script=tmp_path / "gone.sh", debug=False)
