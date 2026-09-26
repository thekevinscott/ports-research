from dataclasses import dataclass

from .coverage_result import CoverageResult


@dataclass(frozen=True)
class SuiteResult:
    """Pass/fail counts from one test suite run.

    `errors` is separate from `failed`: pytest's junit-xml distinguishes a test that
    ran and asserted wrong from one that never ran (an import or fixture blew up
    during collection). Vitest does not surface that distinction at the test level,
    so a vitest-backed result always reports zero errors.

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
