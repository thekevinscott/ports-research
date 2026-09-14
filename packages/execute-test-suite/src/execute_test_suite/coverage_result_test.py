import dataclasses

import pytest

from execute_test_suite.coverage_result import CoverageResult


def describe_coverage_result():
    def it_reports_covered_lines_over_total_as_a_percentage():
        result = CoverageResult(
            covered_lines=3, total_lines=4, covered_branches=0, total_branches=0
        )
        assert result.line_pct == 75.0

    def it_reports_covered_branches_over_total_as_a_percentage():
        result = CoverageResult(
            covered_lines=4, total_lines=4, covered_branches=1, total_branches=4
        )
        assert result.branch_pct == 25.0

    def it_has_no_branch_percentage_for_a_source_that_never_branches():
        result = CoverageResult(
            covered_lines=4, total_lines=4, covered_branches=0, total_branches=0
        )
        assert result.branch_pct is None

    def it_is_frozen():
        result = CoverageResult(
            covered_lines=1, total_lines=1, covered_branches=0, total_branches=0
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.covered_lines = 2
