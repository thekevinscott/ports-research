from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from execute_test_suite.locate_test_suite import locate_test_suite

CACHE_KEY = "abc123"


@pytest.fixture
def settings(tmp_path):
    mock = Mock(
        gbnf_commit="13f1aca",
        prepare_docker_directory=Path("/docker/gbnf-prepare"),
        prepared_directory=tmp_path / "prepared",
    )
    (mock.prepared_directory / CACHE_KEY / "python").mkdir(parents=True)
    (mock.prepared_directory / CACHE_KEY / "javascript").mkdir(parents=True)
    with patch("execute_test_suite.locate_test_suite.settings", mock):
        yield mock


@pytest.fixture
def assemble_whitelist_function():
    with patch("execute_test_suite.locate_test_suite.assemble_whitelist", autospec=True) as m:
        m.return_value = "+ rules"
        yield m


@pytest.fixture
def compute_prepare_cache_key_function():
    with patch(
        "execute_test_suite.locate_test_suite.compute_prepare_cache_key", autospec=True
    ) as m:
        m.return_value = CACHE_KEY
        yield m


def describe_locate_test_suite():
    def it_finds_the_python_tree_prepared_with_every_test(
        settings, assemble_whitelist_function, compute_prepare_cache_key_function
    ):
        assert locate_test_suite("python") == settings.prepared_directory / CACHE_KEY / "python"
        assemble_whitelist_function.assert_called_once_with(
            "python",
            include_unit_tests=True,
            include_source_integration_tests=True,
            include_target_integration_tests=False,
        )
        compute_prepare_cache_key_function.assert_called_once_with(
            settings.gbnf_commit, settings.prepare_docker_directory, "+ rules"
        )

    def it_finds_the_javascript_tree(
        settings, assemble_whitelist_function, compute_prepare_cache_key_function
    ):
        assert (
            locate_test_suite("javascript")
            == settings.prepared_directory / CACHE_KEY / "javascript"
        )
        assert assemble_whitelist_function.call_args.args == ("javascript",)

    def it_finds_typescript_under_the_javascript_tree(
        settings, assemble_whitelist_function, compute_prepare_cache_key_function
    ):
        assert (
            locate_test_suite("typescript")
            == settings.prepared_directory / CACHE_KEY / "javascript"
        )
        assert assemble_whitelist_function.call_args.args == ("javascript",)

    def it_raises_when_the_tree_was_never_prepared(
        settings, assemble_whitelist_function, compute_prepare_cache_key_function
    ):
        compute_prepare_cache_key_function.return_value = "unprepared"
        with pytest.raises(FileNotFoundError):
            locate_test_suite("python")
