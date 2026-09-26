import pytest

from execute_test_suite.locate_test_suite import locate_test_suite


@pytest.fixture
def test_suites_directory(tmp_path):
    directory = tmp_path / "tests"
    (directory / "python").mkdir(parents=True)
    (directory / "typescript").mkdir(parents=True)
    return directory


def describe_locate_test_suite():
    def it_finds_the_python_suite(test_suites_directory):
        assert locate_test_suite(
            "python", test_suites_directory=test_suites_directory
        ) == test_suites_directory / "python"

    def it_finds_the_typescript_suite(test_suites_directory):
        assert locate_test_suite(
            "typescript", test_suites_directory=test_suites_directory
        ) == test_suites_directory / "typescript"

    def it_finds_the_javascript_suite_under_typescript(test_suites_directory):
        assert locate_test_suite(
            "javascript", test_suites_directory=test_suites_directory
        ) == test_suites_directory / "typescript"

    def it_raises_when_the_suite_is_missing(tmp_path):
        with pytest.raises(FileNotFoundError):
            locate_test_suite("python", test_suites_directory=tmp_path / "tests")
