import json
from pathlib import Path

from .suite_result import SuiteResult


def parse_vitest_report(report_path: Path) -> SuiteResult:
    """Turn vitest's `--reporter=json` summary into one SuiteResult.

    A report with zero collected tests and `success: false` means the run never
    got as far as executing a test — a bad alias, a missing entry file — not a
    clean suite. That is raised rather than reported as a zero-zero pass.
    """
    report = json.loads(report_path.read_text())
    total = report["numTotalTests"]
    if total == 0 and not report["success"]:
        raise RuntimeError(f"vitest collected no tests and did not succeed: {report_path}")
    return SuiteResult(
        total=total,
        passed=report["numPassedTests"],
        failed=report["numFailedTests"],
        errors=0,
        skipped=report["numPendingTests"] + report["numTodoTests"],
    )
