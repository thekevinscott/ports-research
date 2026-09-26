from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.export_prepared_tests import export_prepared_tests


@pytest.fixture
def build_prepare_image():
    with patch(
        "gbnf_experiment.prepare_filesystem.export_prepared_tests.build_prepare_image",
        autospec=True,
    ) as m:
        m.return_value = "gbnf-prepare:latest"
        yield m


@pytest.fixture
def docker_module(build_prepare_image):
    with patch(
        "gbnf_experiment.prepare_filesystem.export_prepared_tests.docker", autospec=True
    ) as m:
        yield m


def describe_export_prepared_tests():
    def it_returns_the_tests_directory_it_copied_out(docker_module, tmp_path):
        assert export_prepared_tests(into=tmp_path, debug=False) == tmp_path / "tests"

    def it_copies_the_prepared_tests_out_of_a_container_on_the_image_it_built(
        docker_module, tmp_path
    ):
        export_prepared_tests(into=tmp_path, debug=False)
        docker_module.container.create.assert_called_once_with("gbnf-prepare:latest")
        docker_module.container.copy.assert_called_once_with(
            (docker_module.container.create.return_value, "/prepared/tests"), tmp_path
        )

    def it_removes_the_container_it_copied_from(docker_module, tmp_path):
        export_prepared_tests(into=tmp_path, debug=False)
        docker_module.container.create.return_value.remove.assert_called_once_with()

    def it_removes_the_container_even_when_the_copy_fails(docker_module, tmp_path):
        docker_module.container.copy.side_effect = RuntimeError("no such path")
        with pytest.raises(RuntimeError):
            export_prepared_tests(into=tmp_path, debug=False)
        docker_module.container.create.return_value.remove.assert_called_once_with()

    def it_forwards_debug_to_the_build(docker_module, build_prepare_image, tmp_path):
        export_prepared_tests(into=tmp_path, debug=True)
        build_prepare_image.assert_called_once_with(debug=True)
