import json

from click.testing import CliRunner

from execute_test_suite.cli import cli


def invoke(language, target, *args):
    return CliRunner().invoke(cli, ["--language", language, "--target", str(target), *args])


def describe_cli():
    def it_reports_the_fired_rules_under_adapt(
        settings_derivations_directory, python_flat_target
    ):
        result = invoke("python", python_flat_target, "--adapt")
        assert result.exit_code == 0
        assert json.loads(result.output)["adapt"] == {
            "rules_fired": ["flat_module", "state_add", "exception_eq"]
        }

    def it_reports_the_measured_lines_under_coverage(
        settings_derivations_directory, python_target
    ):
        result = invoke("python", python_target(42), "--coverage")
        assert result.exit_code == 0
        coverage = json.loads(result.output)["coverage"]
        assert coverage["total_lines"] > 0
        assert coverage["line_pct"] == 100

    def it_prints_no_coverage_section_without_the_flag(
        settings_derivations_directory, python_target
    ):
        result = invoke("python", python_target(42))
        assert "coverage" not in json.loads(result.output)

    def it_prints_no_adapt_section_without_the_flag(
        settings_derivations_directory, python_target
    ):
        result = invoke("python", python_target(42))
        assert "adapt" not in json.loads(result.output)

    def it_exits_zero_and_reports_success_for_a_passing_port(
        settings_derivations_directory, python_target
    ):
        result = invoke("python", python_target(42))
        assert result.exit_code == 0
        assert '"success": true' in result.output

    def it_exits_nonzero_and_reports_failure_for_a_failing_port(
        settings_derivations_directory, python_target
    ):
        result = invoke("python", python_target(0))
        assert result.exit_code == 1
        assert '"success": false' in result.output
