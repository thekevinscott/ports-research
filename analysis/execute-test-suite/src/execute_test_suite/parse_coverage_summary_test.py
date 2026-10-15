import json

import pytest

from execute_test_suite.parse_coverage_summary import parse_coverage_summary

TOTAL = {
    "lines": {"total": 1085, "covered": 758, "skipped": 0, "pct": 69.86},
    "statements": {"total": 1085, "covered": 758, "skipped": 0, "pct": 69.86},
    "functions": {"total": 107, "covered": 84, "skipped": 0, "pct": 78.5},
    "branches": {"total": 270, "covered": 215, "skipped": 0, "pct": 79.62},
    "branchesTrue": {"total": 0, "covered": 0, "skipped": 0, "pct": 100},
}


@pytest.fixture
def report_path(tmp_path):
    return tmp_path / "coverage-summary.json"


def write_report(path, **overrides):
    path.write_text(json.dumps({"total": {**TOTAL, **overrides}, "/port/src/index.ts": TOTAL}))


def describe_parse_coverage_summary():
    def it_reads_the_line_counts_from_the_totals(report_path):
        write_report(report_path)
        result = parse_coverage_summary(report_path)
        assert result.covered_lines == 758
        assert result.total_lines == 1085

    def it_reads_the_branch_counts_from_the_totals(report_path):
        write_report(report_path)
        result = parse_coverage_summary(report_path)
        assert result.covered_branches == 215
        assert result.total_branches == 270

    def it_ignores_the_per_file_rows(report_path):
        write_report(report_path)
        assert parse_coverage_summary(report_path).line_pct == 100 * 758 / 1085

    def it_reads_a_run_that_loaded_none_of_the_port_as_zero(report_path):
        """The provider counts only files the tests loaded, so a suite that ran none
        of the port's source reports zero lines."""
        write_report(
            report_path,
            lines={"total": 0, "covered": 0, "skipped": 0, "pct": "Unknown"},
            branches={"total": 0, "covered": 0, "skipped": 0, "pct": "Unknown"},
        )
        result = parse_coverage_summary(report_path)
        assert result.covered_lines == 0
        assert result.total_lines == 0
        assert result.line_pct == 0.0
