import json

import pytest

from execute_test_suite.parse_vitest_report import parse_vitest_report


def write_report(path, **overrides):
    report = {
        "numTotalTests": 5,
        "numPassedTests": 5,
        "numFailedTests": 0,
        "numPendingTests": 0,
        "numTodoTests": 0,
        "success": True,
        "testResults": [],
        **overrides,
    }
    path.write_text(json.dumps(report))


@pytest.fixture
def report_path(tmp_path):
    return tmp_path / "report.json"


def describe_parse_vitest_report():
    def it_counts_an_all_passing_suite(report_path):
        write_report(report_path)
        result = parse_vitest_report(report_path)
        assert result.total == 5
        assert result.passed == 5
        assert result.failed == 0
        assert result.errors == 0
        assert result.skipped == 0

    def it_counts_failures(report_path):
        write_report(report_path, numPassedTests=3, numFailedTests=2, success=False)
        result = parse_vitest_report(report_path)
        assert result.failed == 2

    def it_sums_pending_and_todo_into_skipped(report_path):
        write_report(report_path, numPendingTests=1, numTodoTests=2)
        result = parse_vitest_report(report_path)
        assert result.skipped == 3

    def it_reports_no_error_for_a_file_whose_tests_ran_and_failed(report_path):
        write_report(
            report_path,
            numFailedTests=1,
            success=False,
            testResults=[{"status": "failed", "assertionResults": [{"status": "failed"}]}],
        )
        result = parse_vitest_report(report_path)
        assert result.errors == 0

    def it_counts_each_file_that_failed_before_running_a_test_as_one_error(report_path):
        write_report(
            report_path,
            success=False,
            testResults=[
                {"status": "failed", "assertionResults": []},
                {"status": "failed", "assertionResults": []},
                {"status": "passed", "assertionResults": [{"status": "passed"}]},
            ],
        )
        result = parse_vitest_report(report_path)
        assert result.errors == 2
        assert result.total == 7
        assert result.passed == 5

    def it_reports_a_run_where_every_file_failed_to_load(report_path):
        write_report(
            report_path,
            numTotalTests=0,
            numPassedTests=0,
            success=False,
            testResults=[{"status": "failed", "assertionResults": []}],
        )
        result = parse_vitest_report(report_path)
        assert result.total == 1
        assert result.errors == 1

    def it_raises_when_nothing_was_collected_and_the_run_failed(report_path):
        write_report(report_path, numTotalTests=0, numPassedTests=0, success=False)
        with pytest.raises(RuntimeError):
            parse_vitest_report(report_path)

    def it_does_not_raise_on_a_genuinely_empty_but_successful_suite(report_path):
        write_report(report_path, numTotalTests=0, numPassedTests=0, success=True)
        result = parse_vitest_report(report_path)
        assert result.total == 0
