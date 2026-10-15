import json
from pathlib import Path

from execute_test_suite.coverage_result import CoverageResult


def parse_coverage_json(report_path: Path) -> CoverageResult:
    """Turn coverage.py's `--cov-report=json` totals into one CoverageResult.

    `percent_covered` is left alone: in branch mode coverage.py folds branches into
    it, so the two percentages are derived from the counts instead. A report with no
    statements at all means the measured source was empty — a bad `--cov` path, not
    a port without code — and is raised. A run that executed none of the port
    records no arcs, so coverage.py reports no branch totals; those count as zero.
    """
    totals = json.loads(report_path.read_text())["totals"]
    if not totals["num_statements"]:
        raise RuntimeError(f"coverage measured no statements: {report_path}")
    return CoverageResult(
        covered_lines=totals["covered_lines"],
        total_lines=totals["num_statements"],
        covered_branches=totals.get("covered_branches", 0),
        total_branches=totals.get("num_branches", 0),
    )
