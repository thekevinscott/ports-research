import dataclasses
from pathlib import Path

from .run_pytest_suite import run_pytest_suite
from .run_vitest_suite import run_vitest_suite


def execute_test_suite(
    *,
    language: str,
    target: Path,
    test_suites_directory: Path,
    suite: str | None = None,
    adapt: bool = False,
    coverage: bool = False,
) -> dict:
    """Run language's canonical gbnf test suite against one ported implementation.

    `suite` narrows the run: "integration" is the grammar-fixtures test alone,
    "unit" is everything else, None is the whole suite.

    `adapt` grades through a per-language shim over the port's API surface and adds
    an `adapt.rules_fired` section naming the rules that applied. Off, the report
    is exactly what it was before the flag existed.

    `coverage` measures how much of `target`'s own source the run executed and adds
    a `coverage` section. `branch_pct` is null for a source that never branches.

    `target` is graded, never written to: the suite runs from a scratch directory,
    reading `target` and the suite and writing its report elsewhere.

    A javascript port is graded against the typescript suite: the prepare stage
    only writes a typescript tree, and its vitest specs run through a TS entry shim.

    The lookup is built here, not at module scope: a module-scope dict would
    capture `run_pytest_suite`/`run_vitest_suite` once at import time, so patching
    either name later (as every unit test here does) would silently miss it.
    """
    languages = {
        "python": (run_pytest_suite, "python"),
        "typescript": (run_vitest_suite, "typescript"),
        "javascript": (run_vitest_suite, "typescript"),
    }
    runner, suite_name = languages[language]
    test_suite_directory = test_suites_directory / suite_name
    result = runner(
        test_suite_directory=test_suite_directory,
        target=target,
        suite=suite,
        adapt=adapt,
        coverage=coverage,
    )
    counts = dataclasses.asdict(result)
    rules_fired = counts.pop("rules_fired")
    counts.pop("coverage")
    report = {
        "language": language,
        "suite": suite,
        "target": str(target),
        "test_suite_directory": str(test_suite_directory),
        **counts,
        "success": result.success,
    }
    if adapt:
        report["adapt"] = {"rules_fired": list(rules_fired)}
    if result.coverage is not None:
        report["coverage"] = {
            "line_pct": result.coverage.line_pct,
            "branch_pct": result.coverage.branch_pct,
            "covered_lines": result.coverage.covered_lines,
            "total_lines": result.coverage.total_lines,
        }
    return report
