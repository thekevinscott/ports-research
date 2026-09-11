import json

import pytest

from execute_test_suite.parse_coverage_json import parse_coverage_json

TOTALS = {
    "covered_lines": 720,
    "num_statements": 917,
    "percent_covered": 75.18367346938776,
    "missing_lines": 197,
    "excluded_lines": 2,
    "num_branches": 308,
    "num_partial_branches": 45,
    "covered_branches": 201,
    "missing_branches": 107,
}


@pytest.fixture
def report_path(tmp_path):
    return tmp_path / "coverage.json"


def write_report(path, **overrides):
    path.write_text(json.dumps({"totals": {**TOTALS, **overrides}, "files": {}}))


def describe_parse_coverage_json():
    def it_reads_the_line_counts_from_the_totals(report_path):
        write_report(report_path)
        result = parse_coverage_json(report_path)
        assert result.covered_lines == 720
        assert result.total_lines == 917

    def it_reads_the_branch_counts_from_the_totals(report_path):
        write_report(report_path)
        result = parse_coverage_json(report_path)
        assert result.covered_branches == 201
        assert result.total_branches == 308

    def it_ignores_the_combined_percentage_coverage_py_reports(report_path):
        """coverage.py's own `percent_covered` mixes lines and branches once branch
        mode is on; the line percentage comes from the line counts instead."""
        write_report(report_path)
        assert parse_coverage_json(report_path).line_pct == 100 * 720 / 917

    def it_raises_when_coverage_measured_nothing(report_path):
        write_report(report_path, covered_lines=0, num_statements=0)
        with pytest.raises(RuntimeError):
            parse_coverage_json(report_path)
