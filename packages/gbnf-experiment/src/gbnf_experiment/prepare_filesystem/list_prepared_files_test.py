from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.list_prepared_files import list_prepared_files

LISTING = "reference_implementation/typescript/package.json\ntests/python/validate_test.py\n"


@pytest.fixture
def build_prepare_image():
    with patch(
        "gbnf_experiment.prepare_filesystem.list_prepared_files.build_prepare_image",
        autospec=True,
    ) as m:
        m.return_value = "gbnf-prepare:latest"
        yield m


@pytest.fixture
def docker_module(build_prepare_image):
    with patch(
        "gbnf_experiment.prepare_filesystem.list_prepared_files.docker", autospec=True
    ) as m:
        m.run.return_value = LISTING
        yield m


def describe_list_prepared_files():
    def it_returns_one_entry_per_line_of_the_listing(docker_module):
        assert list_prepared_files(debug=False) == [
            "reference_implementation/typescript/package.json",
            "tests/python/validate_test.py",
        ]

    def it_builds_the_prepare_stage_first(docker_module, build_prepare_image):
        order = []
        build_prepare_image.side_effect = lambda **k: order.append("build") or "gbnf-prepare:latest"
        docker_module.run.side_effect = lambda *a, **k: order.append("run") or LISTING
        list_prepared_files(debug=False)
        assert order == ["build", "run"]

    def it_reads_the_listing_out_of_the_image_it_built(docker_module):
        list_prepared_files(debug=False)
        docker_module.run.assert_called_once_with(
            "gbnf-prepare:latest", ["cat", "/prepared.list"], remove=True
        )

    def it_forwards_debug_to_the_build(docker_module, build_prepare_image):
        list_prepared_files(debug=True)
        build_prepare_image.assert_called_once_with(debug=True)
