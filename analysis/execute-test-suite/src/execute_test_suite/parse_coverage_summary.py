import json
from pathlib import Path

from execute_test_suite.coverage_result import CoverageResult


def parse_coverage_summary(report_path: Path) -> CoverageResult:
    """Turn `@vitest/coverage-v8`'s `json-summary` totals into one CoverageResult.

    The provider counts only files the tests loaded, so a suite that ran none of the
    port's source reports zero lines.
    """
    total = json.loads(report_path.read_text())["total"]
    return CoverageResult(
        covered_lines=total["lines"]["covered"],
        total_lines=total["lines"]["total"],
        covered_branches=total["branches"]["covered"],
        total_branches=total["branches"]["total"],
    )
