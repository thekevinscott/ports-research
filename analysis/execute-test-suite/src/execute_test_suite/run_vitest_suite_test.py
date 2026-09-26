import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from execute_test_suite.coverage_result import CoverageResult
from execute_test_suite.run_vitest_suite import (
    ALL_TESTS_GLOB,
    COVERAGE_PACKAGE,
    INTEGRATION_TEST_GLOB,
    PORT_ENTRY_FILE,
    PORT_SOURCE_GLOB,
    TSCONFIG_RAW,
    VITEST_BIN,
    VITEST_VERSION,
    run_vitest_suite,
)
from execute_test_suite.suite_result import SuiteResult

TARGET = Path("/data/run/ported_implementation")


def output_flag(argv):
    return next(arg for arg in argv if arg.startswith("--outputFile="))


def flag(argv, prefix):
    return next(arg for arg in argv if arg.startswith(prefix)).removeprefix(prefix)


def flags(argv, prefix):
    return [arg.removeprefix(prefix) for arg in argv if arg.startswith(prefix)]


@pytest.fixture
def test_suite_directory(tmp_path):
    directory = tmp_path / "typescript"
    directory.mkdir()
    (directory / "value.test.ts").write_text("// a spec")
    return directory


@pytest.fixture
def captured():
    """State read back while the scratch directory still exists.

    The function tears its scratch directory down before returning, so a test
    reading the scratch directory afterward would find nothing there.
    """
    return {}


@pytest.fixture
def subprocess_module(captured):
    def run(argv, **kwargs):
        if "--config" not in argv:
            captured["install_argv"] = argv
            return Mock(returncode=0, stderr="")
        config_path = Path(argv[argv.index("--config") + 1])
        captured["config_text"] = config_path.read_text()
        captured["copied_spec"] = (
            Path(kwargs["cwd"]) / "tests" / "value.test.ts"
        ).read_text()
        Path(output_flag(argv).removeprefix("--outputFile=")).write_text(
            json.dumps({"numTotalTests": 1, "success": True})
        )
        if any(arg.startswith("--coverage.reportsDirectory=") for arg in argv):
            directory = Path(flag(argv, "--coverage.reportsDirectory="))
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "coverage-summary.json").write_text("{}")
        return Mock(returncode=0, stderr="")

    with patch("execute_test_suite.run_vitest_suite.subprocess", autospec=True) as m:
        m.run.side_effect = run
        yield m


@pytest.fixture
def parse_vitest_report_function():
    with patch("execute_test_suite.run_vitest_suite.parse_vitest_report", autospec=True) as m:
        m.return_value = SuiteResult(total=1, passed=1, failed=0, errors=0, skipped=0)
        yield m


@pytest.fixture
def parse_coverage_summary_function():
    with patch(
        "execute_test_suite.run_vitest_suite.parse_coverage_summary", autospec=True
    ) as m:
        m.return_value = CoverageResult(
            covered_lines=3, total_lines=4, covered_branches=1, total_branches=2
        )
        yield m


@pytest.fixture
def adapt_typescript_function():
    with patch("execute_test_suite.run_vitest_suite.adapt_typescript", autospec=True) as m:
        m.side_effect = lambda directory, **kwargs: directory / "index.ts"
        yield m


@pytest.fixture
def read_adapt_report_function():
    with patch("execute_test_suite.run_vitest_suite.read_adapt_report", autospec=True) as m:
        m.return_value = ("default_export",)
        yield m


def describe_run_vitest_suite():
    def it_returns_the_parsed_report(
        subprocess_module, parse_vitest_report_function, test_suite_directory
    ):
        result = run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        assert result is parse_vitest_report_function.return_value

    def it_parses_the_report_vitest_wrote(
        subprocess_module, parse_vitest_report_function, test_suite_directory
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        argv = subprocess_module.run.call_args.args[0]
        parsed_path = Path(output_flag(argv).removeprefix("--outputFile="))
        assert parse_vitest_report_function.call_args.args == (parsed_path,)

    def it_pins_the_vitest_version(
        subprocess_module, parse_vitest_report_function, test_suite_directory
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        argv = subprocess_module.run.call_args.args[0]
        assert f"vitest@{VITEST_VERSION}" in argv

    def it_runs_through_pnpm_dlx_not_npm(
        subprocess_module, parse_vitest_report_function, test_suite_directory
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        argv = subprocess_module.run.call_args.args[0]
        assert argv[0] == "pnpm"
        assert argv[1] == "dlx"

    def it_copies_the_suite_into_the_scratch_directory(
        subprocess_module, parse_vitest_report_function, test_suite_directory, captured
    ):
        """Copied, not pointed at in place: vite's own `.vite` cache would otherwise
        land inside the read-only derivation cache."""
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        assert captured["copied_spec"] == "// a spec"

    def it_writes_a_config_that_aliases_gbnf_to_the_target_entry_file(
        subprocess_module, parse_vitest_report_function, test_suite_directory, captured
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        assert str(TARGET / PORT_ENTRY_FILE) in captured["config_text"]

    def it_includes_every_spec_and_excludes_nothing_by_default(
        subprocess_module, parse_vitest_report_function, test_suite_directory, captured
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        assert f"include: {json.dumps([ALL_TESTS_GLOB])}" in captured["config_text"]
        assert "exclude: []" in captured["config_text"]

    def it_includes_only_the_grammar_spec_for_the_integration_suite(
        subprocess_module, parse_vitest_report_function, test_suite_directory, captured
    ):
        run_vitest_suite(
            test_suite_directory=test_suite_directory, target=TARGET, suite="integration"
        )
        assert f"include: {json.dumps([INTEGRATION_TEST_GLOB])}" in captured["config_text"]
        assert "exclude: []" in captured["config_text"]

    def it_excludes_the_grammar_spec_for_the_unit_suite(
        subprocess_module, parse_vitest_report_function, test_suite_directory, captured
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET, suite="unit")
        assert f"include: {json.dumps([ALL_TESTS_GLOB])}" in captured["config_text"]
        assert f"exclude: {json.dumps([INTEGRATION_TEST_GLOB])}" in captured["config_text"]

    def it_pins_the_tsconfig_esbuild_reads_rather_than_the_targets(
        subprocess_module, parse_vitest_report_function, test_suite_directory, captured
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        assert f"tsconfigRaw: {json.dumps(TSCONFIG_RAW)}" in captured["config_text"]

    def it_runs_from_a_scratch_directory_not_the_target_or_suite(
        subprocess_module, parse_vitest_report_function, test_suite_directory
    ):
        run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        cwd = subprocess_module.run.call_args.kwargs["cwd"]
        assert Path(cwd) not in (TARGET, test_suite_directory)

    def it_raises_when_vitest_never_produced_a_report(
        parse_vitest_report_function, test_suite_directory
    ):
        with patch("execute_test_suite.run_vitest_suite.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=1, stderr="boom")
            with pytest.raises(RuntimeError):
                run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
        parse_vitest_report_function.assert_not_called()

    def describe_strict():
        def it_writes_no_shim(
            subprocess_module,
            parse_vitest_report_function,
            adapt_typescript_function,
            read_adapt_report_function,
            test_suite_directory,
        ):
            run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
            adapt_typescript_function.assert_not_called()
            read_adapt_report_function.assert_not_called()

        def it_reports_no_fired_rules(
            subprocess_module, parse_vitest_report_function, test_suite_directory
        ):
            result = run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
            assert result.rules_fired == ()

    def describe_adapt():
        def it_writes_the_shim_over_the_target_entry_file_inside_the_scratch_directory(
            subprocess_module,
            parse_vitest_report_function,
            adapt_typescript_function,
            read_adapt_report_function,
            test_suite_directory,
        ):
            run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, adapt=True
            )
            cwd = Path(subprocess_module.run.call_args.kwargs["cwd"])
            kwargs = adapt_typescript_function.call_args.kwargs
            assert adapt_typescript_function.call_args.args[0].is_relative_to(cwd)
            assert kwargs["port_entry"] == TARGET / PORT_ENTRY_FILE
            assert kwargs["report_path"].is_relative_to(cwd)

        def it_aliases_gbnf_to_the_shim_not_the_target(
            subprocess_module,
            parse_vitest_report_function,
            adapt_typescript_function,
            read_adapt_report_function,
            test_suite_directory,
            captured,
        ):
            run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, adapt=True
            )
            shim = adapt_typescript_function.call_args.args[0] / "index.ts"
            assert json.dumps(str(shim)) in captured["config_text"]
            assert str(TARGET / PORT_ENTRY_FILE) not in captured["config_text"]

        def it_reads_the_fired_rules_from_the_shims_report(
            subprocess_module,
            parse_vitest_report_function,
            adapt_typescript_function,
            read_adapt_report_function,
            test_suite_directory,
        ):
            result = run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, adapt=True
            )
            report_path = adapt_typescript_function.call_args.kwargs["report_path"]
            read_adapt_report_function.assert_called_once_with(report_path)
            assert result.rules_fired == ("default_export",)
            assert result.total == 1

    def describe_coverage():
        def it_adds_no_coverage_flags_and_installs_nothing_by_default(
            subprocess_module,
            parse_vitest_report_function,
            parse_coverage_summary_function,
            test_suite_directory,
        ):
            result = run_vitest_suite(test_suite_directory=test_suite_directory, target=TARGET)
            argv = subprocess_module.run.call_args.args[0]
            assert subprocess_module.run.call_count == 1
            assert not any(arg.startswith("--coverage") for arg in argv)
            assert result.coverage is None
            parse_coverage_summary_function.assert_not_called()

        def it_installs_the_provider_pinned_to_the_vitest_version_in_the_scratch_directory(
            subprocess_module,
            parse_vitest_report_function,
            parse_coverage_summary_function,
            test_suite_directory,
            captured,
        ):
            """pnpm dlx puts vitest outside the run's root, where vite cannot resolve the
            provider from; the coverage run installs both into the scratch directory."""
            run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, coverage=True
            )
            install = captured["install_argv"]
            cwd = Path(subprocess_module.run.call_args.kwargs["cwd"])
            assert install[0] == "pnpm"
            assert install[install.index("--dir") + 1] == str(cwd)
            assert f"vitest@{VITEST_VERSION}" in install
            assert f"{COVERAGE_PACKAGE}@{VITEST_VERSION}" in install

        def it_runs_the_scratch_installed_vitest_rather_than_dlx(
            subprocess_module,
            parse_vitest_report_function,
            parse_coverage_summary_function,
            test_suite_directory,
        ):
            run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            cwd = Path(subprocess_module.run.call_args.kwargs["cwd"])
            assert argv[0] == str(cwd / VITEST_BIN)
            assert "dlx" not in argv

        def it_measures_the_ports_own_source_and_excludes_specs(
            subprocess_module,
            parse_vitest_report_function,
            parse_coverage_summary_function,
            test_suite_directory,
        ):
            run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            assert flag(argv, "--coverage.include=") == str(TARGET / PORT_SOURCE_GLOB)
            assert "**/*.test.ts" in flags(argv, "--coverage.exclude=")

        def it_writes_the_coverage_report_into_the_scratch_directory(
            subprocess_module,
            parse_vitest_report_function,
            parse_coverage_summary_function,
            test_suite_directory,
        ):
            run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            cwd = Path(subprocess_module.run.call_args.kwargs["cwd"])
            assert Path(flag(argv, "--coverage.reportsDirectory=")).is_relative_to(cwd)
            assert "json-summary" in flags(argv, "--coverage.reporter=")

        def it_parses_the_summary_vitest_wrote(
            subprocess_module,
            parse_vitest_report_function,
            parse_coverage_summary_function,
            test_suite_directory,
        ):
            result = run_vitest_suite(
                test_suite_directory=test_suite_directory, target=TARGET, coverage=True
            )
            argv = subprocess_module.run.call_args.args[0]
            summary = Path(flag(argv, "--coverage.reportsDirectory=")) / "coverage-summary.json"
            assert parse_coverage_summary_function.call_args.args == (summary,)
            assert result.coverage is parse_coverage_summary_function.return_value
            assert result.total == 1

        def it_reports_coverage_and_fired_rules_together(
            subprocess_module,
            parse_vitest_report_function,
            parse_coverage_summary_function,
            adapt_typescript_function,
            read_adapt_report_function,
            test_suite_directory,
        ):
            result = run_vitest_suite(
                test_suite_directory=test_suite_directory,
                target=TARGET,
                adapt=True,
                coverage=True,
            )
            assert result.coverage is parse_coverage_summary_function.return_value
            assert result.rules_fired == ("default_export",)

        def it_raises_when_the_provider_could_not_be_installed(
            parse_vitest_report_function, parse_coverage_summary_function, test_suite_directory
        ):
            with patch("execute_test_suite.run_vitest_suite.subprocess", autospec=True) as m:
                m.run.return_value = Mock(returncode=1, stderr="no registry")
                with pytest.raises(RuntimeError, match="no registry"):
                    run_vitest_suite(
                        test_suite_directory=test_suite_directory, target=TARGET, coverage=True
                    )
            assert m.run.call_count == 1
            parse_vitest_report_function.assert_not_called()

        def it_raises_when_vitest_never_produced_a_coverage_summary(
            parse_vitest_report_function, parse_coverage_summary_function, test_suite_directory
        ):
            def run(argv, **kwargs):
                if "--config" not in argv:
                    return Mock(returncode=0, stderr="")
                Path(output_flag(argv).removeprefix("--outputFile=")).write_text(
                    json.dumps({"numTotalTests": 1, "success": True})
                )
                return Mock(returncode=1, stderr="boom")

            with patch("execute_test_suite.run_vitest_suite.subprocess", autospec=True) as m:
                m.run.side_effect = run
                with pytest.raises(RuntimeError):
                    run_vitest_suite(
                        test_suite_directory=test_suite_directory, target=TARGET, coverage=True
                    )
            parse_coverage_summary_function.assert_not_called()
