import pytest

from measure_transcript.may_hold_tests import may_hold_tests


def describe_may_hold_tests():
    @pytest.mark.parametrize("origin", ["/input/python/tests", "/input/python", "/input/javascript/src/a.test.ts"])
    def it_accepts_directories_and_test_files(origin):
        assert may_hold_tests(origin) is True

    @pytest.mark.parametrize("origin", ["/input/python/pyproject.toml", "/input/python/Makefile", "/input/javascript/src/a.ts"])
    def it_rejects_config_and_source_files(origin):
        assert may_hold_tests(origin) is False
