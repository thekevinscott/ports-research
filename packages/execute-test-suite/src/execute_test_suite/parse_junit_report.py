from pathlib import Path
from xml.etree import ElementTree

from .suite_result import SuiteResult


def parse_junit_report(report_path: Path) -> SuiteResult:
    """Sum every `<testsuite>` in a pytest junit-xml report into one SuiteResult."""
    root = ElementTree.parse(report_path).getroot()
    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
    total = sum(int(suite.get("tests", 0)) for suite in suites)
    failed = sum(int(suite.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.get("skipped", 0)) for suite in suites)
    return SuiteResult(
        total=total,
        passed=total - failed - errors - skipped,
        failed=failed,
        errors=errors,
        skipped=skipped,
    )
