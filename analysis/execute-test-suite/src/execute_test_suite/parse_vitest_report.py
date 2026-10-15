import json
from pathlib import Path

from execute_test_suite.suite_result import SuiteResult


def parse_vitest_report(report_path: Path) -> SuiteResult:
    """Turn vitest's `--reporter=json` summary into one SuiteResult.

    A test file that failed before running any test — an import that did not resolve,
    a top-level throw — counts as one error, as pytest counts a file it could not
    collect. A run with nothing collected and nothing errored that did not succeed
    never got as far as a test file and is raised.
    """
    report = json.loads(report_path.read_text())
    errors = sum(
        1
        for file in report["testResults"]
        if file["status"] == "failed" and not file["assertionResults"]
    )
    total = report["numTotalTests"] + errors
    if total == 0 and not report["success"]:
        raise RuntimeError(f"vitest collected no tests and did not succeed: {report_path}")
    return SuiteResult(
        total=total,
        passed=report["numPassedTests"],
        failed=report["numFailedTests"],
        errors=errors,
        skipped=report["numPendingTests"] + report["numTodoTests"],
    )
