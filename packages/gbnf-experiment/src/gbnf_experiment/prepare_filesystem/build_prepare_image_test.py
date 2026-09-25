from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.build_prepare_image import build_prepare_image


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.build_prepare_image.settings", autospec=True
    ) as m:
        m.workspace_docker_directory = tmp_path / "docker" / "gbnf-workspace"
        m.prepare_image_tag = "gbnf-prepare:latest"
        m.gbnf_commit = "13f1aca"
        yield m


@pytest.fixture
def docker_module(settings):
    with patch(
        "gbnf_experiment.prepare_filesystem.build_prepare_image.docker", autospec=True
    ) as m:
        yield m


def describe_build_prepare_image():
    def it_returns_the_tag_it_built(docker_module):
        assert build_prepare_image(debug=False) == "gbnf-prepare:latest"

    def it_builds_only_the_prepare_stage_at_the_pin(docker_module, settings):
        build_prepare_image(debug=False)
        docker_module.build.assert_called_once_with(
            settings.workspace_docker_directory,
            target="prepare",
            tags="gbnf-prepare:latest",
            build_args={"GBNF_COMMIT": "13f1aca"},
            progress=False,
        )

    def it_shows_the_build_when_debugging(docker_module):
        build_prepare_image(debug=True)
        assert docker_module.build.call_args.kwargs["progress"] == "tty"
