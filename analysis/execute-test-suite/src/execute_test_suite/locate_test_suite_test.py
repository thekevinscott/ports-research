import pytest

from execute_test_suite.locate_test_suite import locate_test_suite

DERIVATION_CACHE_KEY = "abc123"


@pytest.fixture
def derivations_directory(tmp_path):
    directory = tmp_path / "derivations"
    (directory / DERIVATION_CACHE_KEY / "tests" / "python").mkdir(parents=True)
    (directory / DERIVATION_CACHE_KEY / "tests" / "typescript").mkdir(parents=True)
    return directory


def describe_locate_test_suite():
    def it_finds_the_python_suite(derivations_directory):
        assert locate_test_suite(
            "python",
            derivations_directory=derivations_directory,
            derivation_cache_key=DERIVATION_CACHE_KEY,
        ) == derivations_directory / DERIVATION_CACHE_KEY / "tests" / "python"

    def it_finds_the_typescript_suite(derivations_directory):
        assert locate_test_suite(
            "typescript",
            derivations_directory=derivations_directory,
            derivation_cache_key=DERIVATION_CACHE_KEY,
        ) == derivations_directory / DERIVATION_CACHE_KEY / "tests" / "typescript"

    def it_finds_the_javascript_suite_under_typescript(derivations_directory):
        assert locate_test_suite(
            "javascript",
            derivations_directory=derivations_directory,
            derivation_cache_key=DERIVATION_CACHE_KEY,
        ) == derivations_directory / DERIVATION_CACHE_KEY / "tests" / "typescript"

    def it_raises_when_the_derivation_was_never_prepared(tmp_path):
        with pytest.raises(FileNotFoundError):
            locate_test_suite(
                "python",
                derivations_directory=tmp_path / "derivations",
                derivation_cache_key=DERIVATION_CACHE_KEY,
            )
