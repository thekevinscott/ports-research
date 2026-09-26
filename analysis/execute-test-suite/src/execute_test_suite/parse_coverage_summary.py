import json
from pathlib import Path

from .coverage_result import CoverageResult


def parse_coverage_summary(report_path: Path) -> CoverageResult:
    """Turn `@vitest/coverage-v8`'s `json-summary` totals into one CoverageResult.

    A summary of zero lines is raised rather than reported: the v8 provider writes
    that whenever its include glob matched no file, which looks identical to a run
    that measured a source with nothing in it.
    """
    total = json.loads(report_path.read_text())["total"]
    if not total["lines"]["total"]:
        raise RuntimeError(f"vitest measured no lines: {report_path}")
    return CoverageResult(
        covered_lines=total["lines"]["covered"],
        total_lines=total["lines"]["total"],
        covered_branches=total["branches"]["covered"],
        total_branches=total["branches"]["total"],
    )
