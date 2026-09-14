import pytest

from execute_test_suite.parse_junit_report import parse_junit_report


def write_report(path, *, tests, failures=0, errors=0, skipped=0):
    path.write_text(
        f'<testsuites><testsuite name="pytest" tests="{tests}" failures="{failures}" '
        f'errors="{errors}" skipped="{skipped}"></testsuite></testsuites>'
    )


@pytest.fixture
def report_path(tmp_path):
    return tmp_path / "report.xml"


def describe_parse_junit_report():
    def it_counts_an_all_passing_suite(report_path):
        write_report(report_path, tests=5)
        result = parse_junit_report(report_path)
        assert result.total == 5
        assert result.passed == 5
        assert result.failed == 0
        assert result.errors == 0
        assert result.skipped == 0

    def it_counts_failures(report_path):
        write_report(report_path, tests=5, failures=2)
        result = parse_junit_report(report_path)
        assert result.failed == 2
        assert result.passed == 3

    def it_counts_errors_separately_from_failures(report_path):
        write_report(report_path, tests=5, failures=1, errors=1)
        result = parse_junit_report(report_path)
        assert result.failed == 1
        assert result.errors == 1
        assert result.passed == 3

    def it_counts_skipped(report_path):
        write_report(report_path, tests=5, skipped=2)
        result = parse_junit_report(report_path)
        assert result.skipped == 2
        assert result.passed == 3

    def it_sums_more_than_one_testsuite(tmp_path):
        report_path = tmp_path / "report.xml"
        report_path.write_text(
            "<testsuites>"
            '<testsuite name="a" tests="2" failures="1" errors="0" skipped="0"></testsuite>'
            '<testsuite name="b" tests="3" failures="0" errors="1" skipped="0"></testsuite>'
            "</testsuites>"
        )
        result = parse_junit_report(report_path)
        assert result.total == 5
        assert result.failed == 1
        assert result.errors == 1
