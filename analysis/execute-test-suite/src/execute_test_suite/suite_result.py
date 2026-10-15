from dataclasses import dataclass

from execute_test_suite.coverage_result import CoverageResult


@dataclass(frozen=True)
class SuiteResult:
    """Pass/fail counts from one test suite run.

    `errors` is separate from `failed`: a test that ran and asserted wrong is a
    failure; a test file that never got to run a test (an import or fixture blew up
    during collection) is an error.

    `rules_fired` names the adaptation rules a shim applied; empty on a strict run.
    `coverage` is None unless the run was asked to measure it.
    """

    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    rules_fired: tuple[str, ...] = ()
    coverage: CoverageResult | None = None

    @property
    def success(self) -> bool:
        return self.failed == 0 and self.errors == 0
