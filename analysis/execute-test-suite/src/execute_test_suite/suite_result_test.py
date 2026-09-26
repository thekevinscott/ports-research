import dataclasses

import pytest

from execute_test_suite.suite_result import SuiteResult


def describe_suite_result():
    def it_succeeds_with_no_failures_and_no_errors():
        result = SuiteResult(total=3, passed=3, failed=0, errors=0, skipped=0)
        assert result.success is True

    def it_fails_on_a_failure():
        result = SuiteResult(total=3, passed=2, failed=1, errors=0, skipped=0)
        assert result.success is False

    def it_fails_on_an_error():
        result = SuiteResult(total=3, passed=2, failed=0, errors=1, skipped=0)
        assert result.success is False

    def it_fires_no_adaptation_rules_by_default():
        result = SuiteResult(total=1, passed=1, failed=0, errors=0, skipped=0)
        assert result.rules_fired == ()

    def it_is_frozen():
        result = SuiteResult(total=1, passed=1, failed=0, errors=0, skipped=0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.total = 2
