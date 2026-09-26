import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from execute_test_suite.coverage_result import CoverageResult
from execute_test_suite.run_pytest_suite import (
    ADAPT_PLUGIN,
    COVERAGE_CONFIG_FILE,
    INTEGRATION_TEST_FILE,
    PYTEST_COV_VERSION,
    PYTEST_DESCRIBE_VERSION,
    PYTEST_VERSION,
    REPORT_VARIABLE,
    TARGET_VARIABLE,
    run_pytest_suite,
)
from execute_test_suite.suite_result import SuiteResult

TEST_SUITE_DIRECTORY = Path("/derivations/key/tests/python")
INTEGRATION_TEST = TEST_SUITE_DIRECTORY / INTEGRATION_TEST_FILE
TARGET = Path("/data/run/ported_implementation")


def report_flag(argv):
    return next(arg for arg in argv if arg.startswith("--junit-xml="))


def coverage_flag(argv):
    return next(arg for arg in argv if arg.startswith("--cov-report=json:"))


@pytest.fixture
def captured():
    return {}


@pytest.fixture
def subprocess_module(captured):
    def run(argv, **kwargs):
        Path(report_flag(argv).removeprefix("--junit-xml=")).write_text(
            '<testsuites><testsuite tests="1" failures="0" errors="0" '
            'skipped="0"></testsuite></testsuites>'
        )
        if any(arg.startswith("--cov-report=json:") for arg in argv):
            Path(coverage_flag(argv).removeprefix("--cov-report=json:")).write_text("{}")
            captured["coverage_config"] = (
                Path(kwargs["cwd"]) / COVERAGE_CONFIG_FILE
            ).read_text()
        captured["scratch_files"] = sorted(p.name for p in Path(kwargs["cwd"]).iterdir())
        return Mock(returncode=0, stderr="")

    with patch("execute_test_suite.run_pytest_suite.subprocess", autospec=True) as m:
        m.run.side_effect = run
        yield m


@pytest.fixture
def parse_junit_report_function():
    with patch("execute_test_suite.run_pytest_suite.parse_junit_report", autospec=True) as m:
        m.return_value = SuiteResult(total=1, passed=1, failed=0, errors=0, skipped=0)
        yield m


@pytest.fixture
def parse_coverage_json_function():
    with patch("execute_test_suite.run_pytest_suite.parse_coverage_json", autospec=True) as m:
        m.return_value = CoverageResult(
            covered_lines=3, total_lines=4, covered_branches=1, total_branches=2
        )
        yield m


@pytest.fixture
def read_adapt_report_function():
    with patch("execute_test_suite.run_pytest_suite.read_adapt_report", autospec=True) as m:
        m.return_value = ("flat_module",)
        yield m


def describe_run_pytest_suite():
    def it_returns_the_parsed_report(subprocess_module, parse_junit_report_function):
        result = run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        assert result is parse_junit_report_function.return_value

    def it_parses_the_report_pytest_wrote(subprocess_module, parse_junit_report_function):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        argv = subprocess_module.run.call_args.args[0]
        parsed_path = Path(report_flag(argv).removeprefix("--junit-xml="))
        assert parse_junit_report_function.call_args.args == (parsed_path,)

    def it_pins_pytest_and_pytest_describe(subprocess_module, parse_junit_report_function):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        argv = subprocess_module.run.call_args.args[0]
        assert f"pytest=={PYTEST_VERSION}" in argv
        assert f"pytest-describe=={PYTEST_DESCRIBE_VERSION}" in argv

    def it_runs_the_derivation_cache_test_suite(subprocess_module, parse_junit_report_function):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        argv = subprocess_module.run.call_args.args[0]
        assert str(TEST_SUITE_DIRECTORY) in argv
        assert not any(arg.startswith("--ignore=") for arg in argv)

    def it_runs_only_the_grammar_fixtures_for_the_integration_suite(
        subprocess_module, parse_junit_report_function
    ):
        run_pytest_suite(
            test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, suite="integration"
        )
        argv = subprocess_module.run.call_args.args[0]
        assert str(INTEGRATION_TEST) in argv
        assert str(TEST_SUITE_DIRECTORY) not in argv

    def it_ignores_the_grammar_fixtures_for_the_unit_suite(
        subprocess_module, parse_junit_report_function
    ):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, suite="unit")
        argv = subprocess_module.run.call_args.args[0]
        assert str(TEST_SUITE_DIRECTORY) in argv
        assert f"--ignore={INTEGRATION_TEST}" in argv

    def it_points_pythonpath_at_the_target(subprocess_module, parse_junit_report_function):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        env = subprocess_module.run.call_args.kwargs["env"]
        assert env["PYTHONPATH"] == str(TARGET)

    def it_never_writes_bytecode_into_the_read_only_suite(
        subprocess_module, parse_junit_report_function
    ):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        env = subprocess_module.run.call_args.kwargs["env"]
        assert env["PYTHONDONTWRITEBYTECODE"] == "1"

    def it_disables_the_cache_plugin(subprocess_module, parse_junit_report_function):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        argv = subprocess_module.run.call_args.args[0]
        assert "-p" in argv
        assert "no:cacheprovider" in argv

    def it_runs_from_a_scratch_directory_not_the_target(
        subprocess_module, parse_junit_report_function
    ):
        run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        cwd = subprocess_module.run.call_args.kwargs["cwd"]
        assert Path(cwd) not in (TARGET, TEST_SUITE_DIRECTORY)

    def it_raises_when_pytest_never_produced_a_report(parse_junit_report_function):
        with patch("execute_test_suite.run_pytest_suite.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=1, stderr="boom")
            with pytest.raises(RuntimeError):
                run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
        parse_junit_report_function.assert_not_called()

    def describe_strict():
        def it_loads_no_plugin_and_sets_no_adapt_variables(
            subprocess_module, parse_junit_report_function, read_adapt_report_function, captured
        ):
            run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
            argv = subprocess_module.run.call_args.args[0]
            env = subprocess_module.run.call_args.kwargs["env"]
            assert ADAPT_PLUGIN not in argv
            assert TARGET_VARIABLE not in env
            assert REPORT_VARIABLE not in env
            assert f"{ADAPT_PLUGIN}.py" not in captured["scratch_files"]
            read_adapt_report_function.assert_not_called()

        def it_reports_no_fired_rules(subprocess_module, parse_junit_report_function):
            result = run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
            assert result.rules_fired == ()

    def describe_adapt():
        def it_copies_the_plugin_into_the_scratch_directory_and_loads_it(
            subprocess_module, parse_junit_report_function, read_adapt_report_function, captured
        ):
            run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, adapt=True)
            argv = subprocess_module.run.call_args.args[0]
            assert f"{ADAPT_PLUGIN}.py" in captured["scratch_files"]
            assert argv[argv.index("-p", argv.index("no:cacheprovider")) + 1] == ADAPT_PLUGIN

        def it_keeps_the_target_first_on_pythonpath_and_adds_the_scratch_directory(
            subprocess_module, parse_junit_report_function, read_adapt_report_function
        ):
            run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, adapt=True)
            env = subprocess_module.run.call_args.kwargs["env"]
            cwd = subprocess_module.run.call_args.kwargs["cwd"]
            assert env["PYTHONPATH"] == f"{TARGET}{os.pathsep}{cwd}"

        def it_tells_the_plugin_where_the_target_and_the_report_are(
            subprocess_module, parse_junit_report_function, read_adapt_report_function
        ):
            run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, adapt=True)
            env = subprocess_module.run.call_args.kwargs["env"]
            cwd = subprocess_module.run.call_args.kwargs["cwd"]
            assert env[TARGET_VARIABLE] == str(TARGET)
            assert Path(env[REPORT_VARIABLE]).is_relative_to(cwd)

        def it_reads_the_fired_rules_from_the_plugins_report(
            subprocess_module, parse_junit_report_function, read_adapt_report_function
        ):
            result = run_pytest_suite(
                test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, adapt=True
            )
            env = subprocess_module.run.call_args.kwargs["env"]
            read_adapt_report_function.assert_called_once_with(Path(env[REPORT_VARIABLE]))
            assert result.rules_fired == ("flat_module",)
            assert result.total == 1

    def describe_coverage():
        def it_adds_no_coverage_flag_or_dependency_by_default(
            subprocess_module, parse_junit_report_function, parse_coverage_json_function
        ):
            result = run_pytest_suite(test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET)
            argv = subprocess_module.run.call_args.args[0]
            assert not any(arg.startswith("--cov") for arg in argv)
            assert f"pytest-cov=={PYTEST_COV_VERSION}" not in argv
            assert result.coverage is None
            parse_coverage_json_function.assert_not_called()

        def it_pins_pytest_cov(
            subprocess_module, parse_junit_report_function, parse_coverage_json_function
        ):
            run_pytest_suite(
                test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            assert f"pytest-cov=={PYTEST_COV_VERSION}" in argv

        def it_measures_the_target(
            subprocess_module, parse_junit_report_function, parse_coverage_json_function
        ):
            run_pytest_suite(
                test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            assert f"--cov={TARGET}" in argv

        def it_writes_the_coverage_report_and_config_into_the_scratch_directory(
            subprocess_module, parse_junit_report_function, parse_coverage_json_function
        ):
            run_pytest_suite(
                test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            cwd = Path(subprocess_module.run.call_args.kwargs["cwd"])
            report = Path(coverage_flag(argv).removeprefix("--cov-report=json:"))
            config = Path(
                next(arg for arg in argv if arg.startswith("--cov-config=")).removeprefix(
                    "--cov-config="
                )
            )
            assert report.is_relative_to(cwd)
            assert config.is_relative_to(cwd)

        def it_turns_on_branch_coverage_and_omits_the_ports_own_tests(
            subprocess_module, parse_junit_report_function, parse_coverage_json_function, captured
        ):
            run_pytest_suite(
                test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, coverage=True
            )
            assert "branch = True" in captured["coverage_config"]
            assert "*_test.py" in captured["coverage_config"]

        def it_parses_the_coverage_report_pytest_wrote(
            subprocess_module, parse_junit_report_function, parse_coverage_json_function
        ):
            result = run_pytest_suite(
                test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            parsed = Path(coverage_flag(argv).removeprefix("--cov-report=json:"))
            assert parse_coverage_json_function.call_args.args == (parsed,)
            assert result.coverage is parse_coverage_json_function.return_value
            assert result.total == 1

        def it_reports_coverage_and_fired_rules_together(
            subprocess_module,
            parse_junit_report_function,
            parse_coverage_json_function,
            read_adapt_report_function,
        ):
            result = run_pytest_suite(
                test_suite_directory=TEST_SUITE_DIRECTORY,
                target=TARGET,
                adapt=True,
                coverage=True,
            )
            assert result.coverage is parse_coverage_json_function.return_value
            assert result.rules_fired == ("flat_module",)

        def it_raises_when_pytest_never_produced_a_coverage_report(
            parse_junit_report_function, parse_coverage_json_function
        ):
            def run(argv, **kwargs):
                Path(report_flag(argv).removeprefix("--junit-xml=")).write_text(
                    '<testsuites><testsuite tests="1" failures="0" errors="0" '
                    'skipped="0"></testsuite></testsuites>'
                )
                return Mock(returncode=1, stderr="boom")

            with patch("execute_test_suite.run_pytest_suite.subprocess", autospec=True) as m:
                m.run.side_effect = run
                with pytest.raises(RuntimeError):
                    run_pytest_suite(
                        test_suite_directory=TEST_SUITE_DIRECTORY, target=TARGET, coverage=True
                    )
            parse_coverage_json_function.assert_not_called()
