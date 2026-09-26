import dataclasses
from pathlib import Path
from unittest.mock import patch

import pytest

from execute_test_suite.coverage_result import CoverageResult
from execute_test_suite.execute_test_suite import execute_test_suite
from execute_test_suite.suite_result import SuiteResult

TEST_SUITES_DIRECTORY = Path("/tmp/scratch/tests")
TARGET = Path("/data/run/ported_implementation")


@pytest.fixture
def suite_result():
    return SuiteResult(total=4, passed=3, failed=1, errors=0, skipped=0)


@pytest.fixture
def run_pytest_suite_function(suite_result):
    with patch("execute_test_suite.execute_test_suite.run_pytest_suite", autospec=True) as m:
        m.return_value = suite_result
        yield m


@pytest.fixture
def run_vitest_suite_function(suite_result):
    with patch("execute_test_suite.execute_test_suite.run_vitest_suite", autospec=True) as m:
        m.return_value = suite_result
        yield m


def call(**overrides):
    return execute_test_suite(
        **{
            "language": "python",
            "target": TARGET,
            "test_suites_directory": TEST_SUITES_DIRECTORY,
            **overrides,
        }
    )


def describe_execute_test_suite():
    def it_runs_python_ports_through_pytest(
        run_pytest_suite_function, run_vitest_suite_function
    ):
        call(language="python")
        run_pytest_suite_function.assert_called_once_with(
            test_suite_directory=TEST_SUITES_DIRECTORY / "python",
            target=TARGET,
            suite=None,
            adapt=False,
            coverage=False,
        )
        run_vitest_suite_function.assert_not_called()

    def it_runs_typescript_ports_through_vitest(
        run_pytest_suite_function, run_vitest_suite_function
    ):
        call(language="typescript")
        run_vitest_suite_function.assert_called_once_with(
            test_suite_directory=TEST_SUITES_DIRECTORY / "typescript",
            target=TARGET,
            suite=None,
            adapt=False,
            coverage=False,
        )
        run_pytest_suite_function.assert_not_called()

    def it_runs_javascript_ports_through_vitest_against_the_typescript_suite(
        run_pytest_suite_function, run_vitest_suite_function
    ):
        call(language="javascript")
        run_vitest_suite_function.assert_called_once_with(
            test_suite_directory=TEST_SUITES_DIRECTORY / "typescript",
            target=TARGET,
            suite=None,
            adapt=False,
            coverage=False,
        )

    def it_forwards_the_suite_to_the_runner(
        run_pytest_suite_function
    ):
        call(suite="unit")
        assert run_pytest_suite_function.call_args.kwargs["suite"] == "unit"

    def it_forwards_adapt_to_the_runner(run_pytest_suite_function):
        call(adapt=True)
        assert run_pytest_suite_function.call_args.kwargs["adapt"] is True

    def it_forwards_coverage_to_the_runner(
        run_pytest_suite_function
    ):
        call(coverage=True)
        assert run_pytest_suite_function.call_args.kwargs["coverage"] is True

    def it_omits_the_coverage_section_from_a_report_taken_without_it(
        run_pytest_suite_function
    ):
        report = call()
        assert "coverage" not in report

    def it_reports_the_line_and_branch_percentages_under_coverage(
        run_pytest_suite_function, suite_result
    ):
        run_pytest_suite_function.return_value = dataclasses.replace(
            suite_result,
            coverage=CoverageResult(
                covered_lines=3, total_lines=4, covered_branches=1, total_branches=2
            ),
        )
        report = call(coverage=True)
        assert report["coverage"] == {
            "line_pct": 75.0,
            "branch_pct": 50.0,
            "covered_lines": 3,
            "total_lines": 4,
        }

    def it_reports_no_branch_percentage_for_a_source_that_never_branches(
        run_pytest_suite_function, suite_result
    ):
        run_pytest_suite_function.return_value = dataclasses.replace(
            suite_result,
            coverage=CoverageResult(
                covered_lines=4, total_lines=4, covered_branches=0, total_branches=0
            ),
        )
        assert call(coverage=True)["coverage"]["branch_pct"] is None

    def it_omits_the_adapt_section_from_a_strict_report(
        run_pytest_suite_function
    ):
        report = call()
        assert "adapt" not in report
        assert "rules_fired" not in report

    def it_reports_the_fired_rules_under_adapt(
        run_pytest_suite_function, suite_result
    ):
        run_pytest_suite_function.return_value = dataclasses.replace(
            suite_result, rules_fired=("flat_module", "state_add")
        )
        report = call(adapt=True)
        assert report["adapt"] == {"rules_fired": ["flat_module", "state_add"]}
        assert "rules_fired" not in report

    def it_reports_an_empty_rule_list_when_the_shim_changed_nothing(
        run_pytest_suite_function
    ):
        assert call(adapt=True)["adapt"] == {"rules_fired": []}

    def it_reports_the_language_and_target(run_pytest_suite_function):
        report = call()
        assert report["language"] == "python"
        assert report["target"] == str(TARGET)

    def it_reports_the_suite(run_pytest_suite_function):
        assert call()["suite"] is None
        assert call(suite="integration")["suite"] == "integration"

    def it_reports_which_test_suite_directory_it_ran(
        run_pytest_suite_function
    ):
        report = call()
        assert report["test_suite_directory"] == str(TEST_SUITES_DIRECTORY / "python")

    def it_flattens_the_suite_result_counts_into_the_report(
        run_pytest_suite_function, suite_result
    ):
        report = call()
        assert report["total"] == suite_result.total
        assert report["passed"] == suite_result.passed
        assert report["failed"] == suite_result.failed
        assert report["errors"] == suite_result.errors
        assert report["skipped"] == suite_result.skipped

    def it_reports_success_from_the_suite_result(
        run_pytest_suite_function, suite_result
    ):
        report = call()
        assert report["success"] == suite_result.success
